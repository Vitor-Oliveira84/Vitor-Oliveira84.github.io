#!/usr/bin/env python3
"""Flag Hunter - Busca automática de flags em múltiplos formatos e técnicas.

Uso:
  python flag-hunter.py <arquivo>              # Análise completa
  python flag-hunter.py <arquivo> --quick      # Apenas triagem rápida
  python flag-hunter.py <diretório> --recursive # Varre todos os arquivos
  python flag-hunter.py <arquivo> --verbose    # Output detalhado
"""
import os
import re
import sys
import struct
import binascii
import base64
from pathlib import Path

FLAG_PATTERNS = [
    rb"(?i)(FirstFlag|academy|picoCTF|THM|HTB|flag|css|ctf|FLAG)\{[^}\n]{1,200}\}",
    rb"(?i)(flag|FLAG)[:=\s]+([A-Za-z0-9_\-\{\}@\.\/:]+)",
    rb"(?i)(password|passwd|pwd)[:=\s]+([A-Za-z0-9_\-\{\}@\.\/:]+)",
]

MAGICS = {
    b"\x89PNG\r\n\x1a\n": "PNG", b"\xff\xd8\xff": "JPEG", b"GIF8": "GIF",
    b"PK\x03\x04": "ZIP/DOCX/JAR", b"Rar!": "RAR", b"7z\xbc\xaf": "7z",
    b"\x1f\x8b\x08": "GZIP", b"%PDF": "PDF", b"\x7fELF": "ELF", b"MZ": "PE/EXE",
    b"\x00\x00\x01\x00": "ICO", b"SQLite format 3": "SQLite", b"BM": "BMP",
}

class FlagHunter:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.flags_found = []
        self.suspicious = []

    def hunt(self, filepath):
        """Busca flags em um arquivo."""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"❌ Erro ao ler {filepath}: {e}")
            return

        print(f"\n{'='*70}")
        print(f"🔍 Analisando: {os.path.basename(filepath)} ({len(data)} bytes)")
        print(f"{'='*70}")

        # 1. Magic bytes
        real_type = next((v for k, v in MAGICS.items() if data.startswith(k)), "desconhecido")
        print(f"📋 Tipo real: {real_type} | Primeiros bytes: {data[:16].hex()}")

        # 2. Busca direta de flags
        self._search_flags(data, "dados brutos")

        # 3. Análise específica por tipo
        if data.startswith(b"\x89PNG"):
            self._analyze_png(filepath, data)
        elif data.startswith(b"\xff\xd8"):
            self._analyze_jpeg(filepath, data)
        elif data.startswith(b"\x7fELF"):
            self._analyze_elf(data)

        # 4. Strings ASCII suspeitas
        self._extract_suspicious_strings(data)

        # 5. Dados embutidos
        self._check_embedded_files(data)

    def _search_flags(self, data, source):
        """Busca padrões de flag."""
        for pattern in FLAG_PATTERNS:
            for m in re.finditer(pattern, data):
                flag = m.group().decode(errors='replace')
                self.flags_found.append((source, flag))
                print(f"✅ FLAG ENCONTRADA [{source}]: {flag}")

    def _analyze_png(self, filepath, data):
        """Análise específica de PNG."""
        if self.verbose:
            print("  📊 Analisando chunks PNG...")
        o = 8
        while o + 8 <= len(data):
            l = struct.unpack(">I", data[o:o+4])[0]
            t = data[o+4:o+8].decode("ascii", "replace")
            if t in ("tEXt", "iTXt", "zTXt", "eXIf", "COM"):
                chunk_data = data[o+8:o+8+l]
                self._search_flags(chunk_data, f"PNG chunk {t}")
            o += 12 + l
            if t == "IEND":
                break

        # Dados após IEND
        eoi = data.rfind(b"\x89PNG") + data[data.rfind(b"\x89PNG"):].find(b"\x49\x45\x4e\x44")
        if eoi > 0 and eoi + 8 < len(data):
            extra = data[eoi+8:]
            if extra and len(extra) > 10:
                print(f"  🔎 {len(extra)} bytes após IEND")
                self._search_flags(extra, "dados após PNG")

    def _analyze_jpeg(self, filepath, data):
        """Análise específica de JPEG."""
        if self.verbose:
            print("  📊 Analisando segmentos JPEG...")
        o = 2
        while o < len(data) and data[o] == 0xFF:
            m = data[o+1]
            if m == 0xDA:
                break
            l = struct.unpack(">H", data[o+2:o+4])[0]
            body = data[o+4:o+2+l]
            if m in (0xFE, 0xE1):  # COM, EXIF
                tag = "COM (comentário)" if m == 0xFE else "EXIF"
                self._search_flags(body, f"JPEG {tag}")
            o += 2 + l

    def _analyze_elf(self, data):
        """Análise específica de ELF."""
        if self.verbose:
            print("  📊 Analisando strings do ELF...")
        for m in re.finditer(rb"[\x20-\x7e]{6,}", data):
            s = m.group().decode(errors='replace')
            if re.search(r'(?i)(flag|password|secret|admin|key)', s):
                self.suspicious.append(s)
                print(f"  🔎 String suspeita: {s}")

    def _extract_suspicious_strings(self, data):
        """Extrai strings que parecem importantes."""
        found_any = False
        for m in re.finditer(rb"[\x20-\x7e]{8,}", data):
            s = m.group().decode(errors='replace')
            if re.search(r'(?i)(pass|pwd|secret|key|admin|token|api|auth|login|user)', s):
                if not found_any:
                    print(f"  🔐 Strings potencialmente sensíveis:")
                    found_any = True
                print(f"     • {s}")
                self.suspicious.append(s)

    def _check_embedded_files(self, data):
        """Procura arquivos embutidos."""
        print(f"  📦 Procurando arquivos embutidos...")
        for sig, name in list(MAGICS.items())[:10]:
            count = 0
            for m in re.finditer(re.escape(sig), data):
                if m.start() > 0:
                    count += 1
            if count > 0:
                print(f"     • {name}: encontrado em offset {data.find(sig)}")

    def report(self):
        """Relatório final."""
        print(f"\n{'='*70}")
        print(f"📊 RELATÓRIO FINAL")
        print(f"{'='*70}")
        if self.flags_found:
            print(f"✅ FLAGS ENCONTRADAS ({len(self.flags_found)}):")
            for source, flag in self.flags_found:
                print(f"   [{source}] {flag}")
        else:
            print(f"⚠️  Nenhuma flag encontrada nos padrões conhecidos")

        if self.suspicious:
            print(f"\n🔐 STRINGS SUSPEITAS ({len(self.suspicious)}):")
            for s in list(set(self.suspicious))[:10]:
                print(f"   • {s}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    filepath = sys.argv[1]
    verbose = '--verbose' in sys.argv
    recursive = '--recursive' in sys.argv

    hunter = FlagHunter(verbose=verbose)

    if recursive and os.path.isdir(filepath):
        print(f"🔄 Modo recursivo: varrendo {filepath}...")
        for root, dirs, files in os.walk(filepath):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    hunter.hunt(full_path)
                except Exception as e:
                    print(f"❌ Erro em {full_path}: {e}")
    else:
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return
        hunter.hunt(filepath)

    hunter.report()

if __name__ == "__main__":
    main()
