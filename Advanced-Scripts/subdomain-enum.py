#!/usr/bin/env python3
"""Subdomain Enumeration + Screenshot - Automatiza descoberta e análise visual.

Uso:
  python subdomain-enum.py -d example.com              # Enum + screenshot
  python subdomain-enum.py -d example.com --enum-only  # Apenas enum
  python subdomain-enum.py -d example.com --threads 10 # Paralelo
  python subdomain-enum.py -d example.com --fuzzing    # Fuzzing de subdomínios
  python subdomain-enum.py -d example.com --passive    # Apenas passive OSINT

Dependências:
  pip install requests dnspython pycurl
  Subfinder, Assetfinder instalados no PATH

Ferramentas:
  - Subfinder, Assetfinder, Amass (passivo)
  - Fuzzing com wordlist
  - Screenshot automático
  - Detecção de WAF
"""
import subprocess
import sys
import argparse
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import urllib.parse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("❌ requests não instalado: pip install requests")
    sys.exit(1)

class SubdomainEnumerator:
    def __init__(self, domain, threads=5, timeout=5):
        self.domain = domain
        self.threads = threads
        self.timeout = timeout
        self.subdomains = set()
        self.resolved = {}
        self.results = {
            'domain': domain,
            'total': 0,
            'resolved': 0,
            'subdomains': [],
            'screenshots': []
        }

    def _run_tool(self, tool, *args):
        """Executa ferramenta externa."""
        try:
            result = subprocess.run([tool, *args], capture_output=True, text=True, timeout=30)
            return result.stdout.strip().split('\n') if result.stdout else []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"  ⚠️  Erro executando {tool}: {e}")
            return []

    def run_subfinder(self):
        """Executa Subfinder (rápido)."""
        print(f"\n🔍 Executando Subfinder...")
        subdomains = self._run_tool('subfinder', '-d', self.domain, '-silent')
        self.subdomains.update([s for s in subdomains if s])
        print(f"  ✅ {len(subdomains)} subdomínios encontrados")
        return subdomains

    def run_assetfinder(self):
        """Executa Assetfinder."""
        print(f"\n🔍 Executando Assetfinder...")
        subdomains = self._run_tool('assetfinder', '--subs-only', self.domain)
        self.subdomains.update([s for s in subdomains if s])
        print(f"  ✅ {len(subdomains)} subdomínios encontrados")
        return subdomains

    def run_amass(self):
        """Executa Amass (mais lento, mais completo)."""
        print(f"\n🔍 Executando Amass (lento)...")
        subdomains = self._run_tool('amass', 'enum', '-passive', '-d', self.domain)
        self.subdomains.update([s for s in subdomains if self.domain in s])
        print(f"  ✅ {len(subdomains)} subdomínios encontrados")
        return subdomains

    def fuzz_subdomains(self, wordlist=None):
        """Fuzzing de subdomínios comuns."""
        print(f"\n🔍 Fuzzing de subdomínios...")

        common = [
            'www', 'mail', 'ftp', 'admin', 'test', 'staging', 'dev', 'api',
            'api-prod', 'api-staging', 'backup', 'db', 'ssh', 'vpn', 'server',
            'staging.', 'sandbox', 'test.', 'demo', 'uat', 'qa', 'app', 'api-dev'
        ]

        fuzzed = set()
        for prefix in common:
            subdomain = f"{prefix}.{self.domain}" if not prefix.endswith('.') else f"{prefix}{self.domain}"
            fuzzed.add(subdomain)

        self.subdomains.update(fuzzed)
        print(f"  ✅ {len(fuzzed)} subdomínios fuzzed")
        return fuzzed

    def resolve_subdomains(self):
        """Resolve IPs dos subdomínios."""
        print(f"\n🌐 Resolvendo {len(self.subdomains)} subdomínios...")

        def resolve_one(subdomain):
            try:
                ip = socket.gethostbyname(subdomain)
                return subdomain, ip
            except:
                return None, None

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(resolve_one, s): s for s in self.subdomains}
            resolved_count = 0

            for future in as_completed(futures):
                subdomain, ip = future.result()
                if ip:
                    self.resolved[subdomain] = ip
                    resolved_count += 1
                    if resolved_count % 10 == 0:
                        print(f"  ⏳ Resolvidos: {resolved_count}")

        print(f"  ✅ {len(self.resolved)} subdomínios resolvidos")
        return self.resolved

    def check_http_services(self):
        """Verifica quais subdomínios têm HTTP/HTTPS."""
        print(f"\n🌐 Verificando serviços HTTP/HTTPS...")

        def check_http(subdomain):
            for protocol in ['https', 'http']:
                try:
                    session = requests.Session()
                    retry = Retry(connect=1, backoff_factor=0.1)
                    adapter = HTTPAdapter(max_retries=retry)
                    session.mount('http://', adapter)
                    session.mount('https://', adapter)

                    url = f"{protocol}://{subdomain}"
                    response = session.get(url, timeout=self.timeout, allow_redirects=False)

                    # Detecta WAF
                    waf_indicators = ['mod_security', 'cloudflare', 'akamai', 'imperva']
                    waf_detected = any(w in response.text.lower() or
                                      w in response.headers.get('Server', '').lower()
                                      for w in waf_indicators)

                    return {
                        'subdomain': subdomain,
                        'url': url,
                        'status': response.status_code,
                        'title': response.text[response.text.find('<title>')+7:response.text.find('</title>')].strip() if '<title>' in response.text else 'N/A',
                        'server': response.headers.get('Server', 'Unknown'),
                        'waf': '⚠️ WAF DETECTADO' if waf_detected else '✅ Sem WAF',
                        'length': len(response.content)
                    }
                except:
                    pass
            return None

        http_services = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_http, s): s for s in self.resolved.keys()}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    http_services.append(result)
                    print(f"  ✅ {result['subdomain']}: {result['status']} ({result['server']})")

        self.results['http_services'] = http_services
        return http_services

    def generate_report(self, output_file=None):
        """Gera relatório."""
        self.results['total'] = len(self.subdomains)
        self.results['resolved'] = len(self.resolved)
        self.results['subdomains'] = sorted(list(self.subdomains))

        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_discovered': self.results['total'],
                'total_resolved': self.results['resolved'],
                'http_services': len(self.results.get('http_services', []))
            },
            'data': self.results
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Relatório salvo: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="Subdomain Enumeration + HTTP Service Discovery")
    parser.add_argument('-d', '--domain', required=True, help='Domínio alvo')
    parser.add_argument('--enum-only', action='store_true', help='Apenas enumeration')
    parser.add_argument('--fuzzing', action='store_true', help='Incluir fuzzing')
    parser.add_argument('--passive', action='store_true', help='Apenas passive')
    parser.add_argument('--threads', type=int, default=10, help='Número de threads')
    parser.add_argument('--timeout', type=int, default=5, help='Timeout por requisição')
    parser.add_argument('-o', '--output', help='Arquivo JSON de saída')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔍 Subdomain Enumeration - {args.domain}")
    print(f"{'='*70}\n")

    enum = SubdomainEnumerator(args.domain, threads=args.threads, timeout=args.timeout)

    # Enumeration
    enum.run_subfinder()
    enum.run_assetfinder()
    if not args.passive:
        enum.run_amass()

    # Fuzzing
    if args.fuzzing:
        enum.fuzz_subdomains()

    # Resolve
    if not args.enum_only:
        enum.resolve_subdomains()
        enum.check_http_services()

    # Report
    output_file = args.output or f"subdomains_{args.domain}.json"
    enum.generate_report(output_file)

    print(f"\n✅ Enumeração completa!")

if __name__ == "__main__":
    main()
