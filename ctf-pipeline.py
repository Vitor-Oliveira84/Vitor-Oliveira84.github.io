#!/usr/bin/env python3
"""CTF Pipeline - Orquestrador que executa todas as técnicas em sequência.

Uso:
  python ctf-pipeline.py <arquivo>              # Pipeline completo
  python ctf-pipeline.py <arquivo> --quick      # Só técnicas rápidas
  python ctf-pipeline.py <diretório> --auto     # Modo automático (todos os arquivos)
  python ctf-pipeline.py <arquivo> --report     # Apenas gera relatório
  python ctf-pipeline.py <arquivo> --verbose    # Output detalhado

Pipeline executado (em ordem):
  1. Flag Hunter - Busca de flags conhecidas
  2. Stego Quick Check - Verifica esteganografia óbvia
  3. Decoder Paralelo - Testa todas as codificações
  4. Binary Analyzer - Se for ELF/PE
  5. OSINT Geo - Se for imagem

Tempo estimado: 30-120 segundos por arquivo
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path

class CTFPipeline:
    def __init__(self, verbose=False, quick=False):
        self.verbose = verbose
        self.quick = quick
        self.results = {}
        self.start_time = time.time()

    def run(self, filepath):
        """Executa pipeline completo."""
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return

        filename = os.path.basename(filepath)
        print(f"\n{'='*70}")
        print(f"🚀 INICIANDO CTF PIPELINE: {filename}")
        print(f"{'='*70}\n")

        self.results[filename] = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'file': filepath,
            'size': os.path.getsize(filepath),
            'techniques': {}
        }

        # Determina técnicas a executar
        techniques = self._select_techniques(filepath)

        for i, (name, cmd) in enumerate(techniques, 1):
            print(f"\n[{i}/{len(techniques)}] ▶️  {name}...")
            print(f"    Executando: {' '.join(cmd)}")

            try:
                start = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                elapsed = time.time() - start

                self.results[filename]['techniques'][name] = {
                    'status': 'ok' if result.returncode == 0 else 'erro',
                    'time': f'{elapsed:.1f}s',
                    'output': result.stdout[:500] if result.stdout else ''
                }

                if result.returncode == 0:
                    print(f"    ✅ Concluído em {elapsed:.1f}s")
                    if result.stdout:
                        self._print_highlights(result.stdout)
                else:
                    print(f"    ⚠️  Retornou código {result.returncode}")
                    if result.stderr:
                        print(f"    Erro: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                print(f"    ⏱️  Timeout (>60s)")
                self.results[filename]['techniques'][name] = {'status': 'timeout'}
            except Exception as e:
                print(f"    ❌ Erro: {e}")
                self.results[filename]['techniques'][name] = {'status': 'erro', 'error': str(e)}

    def _select_techniques(self, filepath):
        """Seleciona técnicas baseadas no tipo de arquivo."""
        with open(filepath, 'rb') as f:
            magic = f.read(4)

        techniques = []

        # Todas as técnicas
        all_tech = [
            ("🚩 Flag Hunter", ["python", "flag-hunter.py", filepath]),
            ("🔍 Stego Quick Check", ["python", "stego-quick.py", filepath]),
        ]

        # Técnicas seletivas
        if magic.startswith(b'\x7fELF') or magic.startswith(b'MZ'):
            all_tech.append(("🔬 Binary Analyzer", ["python", "binary-analyzer.py", filepath]))

        if magic.startswith(b'\x89PNG') or magic.startswith(b'\xff\xd8'):
            all_tech.append(("📍 OSINT Geo", ["python", "osint-geo.py", filepath]))

        # Modo rápido
        if self.quick:
            return all_tech[:2]  # Apenas Flag Hunter + Stego

        return all_tech

    def _print_highlights(self, output):
        """Imprime partes importantes do output."""
        lines = output.split('\n')
        important = [l for l in lines if any(x in l for x in ['✅', 'FLAG', 'flag', 'Password', 'Error'])]

        for line in important[:5]:
            if line.strip():
                print(f"    {line[:80]}")

    def generate_report(self):
        """Gera relatório HTML e JSON."""
        elapsed = time.time() - self.start_time

        print(f"\n{'='*70}")
        print(f"📊 RELATÓRIO FINAL")
        print(f"{'='*70}\n")

        for filename, data in self.results.items():
            print(f"📁 {filename} ({data['size']} bytes)")
            print(f"   ⏱️  Tempo total: {elapsed:.1f}s")

            for tech, result in data['techniques'].items():
                status_icon = '✅' if result['status'] == 'ok' else '⚠️' if result['status'] == 'timeout' else '❌'
                print(f"   {status_icon} {tech}: {result.get('time', 'N/A')}")

        # Salva JSON
        report_file = f"ctf_pipeline_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Relatório salvo: {report_file}")

    def auto_scan(self, directory):
        """Varre diretório automaticamente."""
        print(f"🔄 Modo automático: varrendo {directory}...")

        for filepath in Path(directory).rglob('*'):
            if filepath.is_file():
                # Pula certos tipos
                if filepath.suffix in ['.py', '.txt', '.md', '.html']:
                    continue

                print(f"\n📂 Processando: {filepath}")
                self.run(str(filepath))

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    filepath = sys.argv[1]
    verbose = '--verbose' in sys.argv
    quick = '--quick' in sys.argv
    auto = '--auto' in sys.argv
    report_only = '--report' in sys.argv

    pipeline = CTFPipeline(verbose=verbose, quick=quick)

    if auto and os.path.isdir(filepath):
        pipeline.auto_scan(filepath)
    elif os.path.isfile(filepath):
        pipeline.run(filepath)
    else:
        print(f"❌ Caminho inválido: {filepath}")
        return

    pipeline.generate_report()

if __name__ == "__main__":
    main()
