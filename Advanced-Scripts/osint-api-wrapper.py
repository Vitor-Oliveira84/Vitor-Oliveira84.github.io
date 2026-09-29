#!/usr/bin/env python3
"""OSINT API Wrapper - Shodan, VirusTotal, DNSDumpster, CertSpotter

Uso:
  python osint-api-wrapper.py --shodan "192.168.1.1"
  python osint-api-wrapper.py --virustotal "example.com"
  python osint-api-wrapper.py --domains "example.com"
  python osint-api-wrapper.py --full-recon "example.com"

Dependências:
  pip install shodan requests dnspython

APIs:
  - Shodan (IP/hostname enumeration)
  - VirusTotal (hash/domain/IP reputation)
  - Cert.sh (Certificate transparency)
  - WHOIS (Domain information)
"""
import sys
import argparse
import json
import requests
import time
from datetime import datetime

# Validação de dependências
try:
    import shodan
except ImportError:
    print("⚠️  shodan: pip install shodan")

class OSINTWrapper:
    def __init__(self, shodan_key=None, virustotal_key=None):
        self.shodan_key = shodan_key or os.getenv('SHODAN_API_KEY')
        self.vt_key = virustotal_key or os.getenv('VT_API_KEY')
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'target': None,
            'shodan': {},
            'virustotal': {},
            'certificates': [],
            'dns': {},
            'whois': {}
        }

    def search_shodan(self, query, limit=100):
        """Busca Shodan."""
        if not self.shodan_key:
            print("[!] Shodan API key não configurada")
            return []

        print(f"\n🔍 Shodan: {query}")
        try:
            api = shodan.Shodan(self.shodan_key)
            results = api.search(query, limit=limit)

            print(f"[+] {results['total']} resultados encontrados")

            for result in results['matches'][:10]:
                print(f"  • {result['ip_str']}:{result.get('port')} - {result.get('org', 'Unknown')}")
                self.results['shodan'][result['ip_str']] = {
                    'port': result.get('port'),
                    'service': result.get('product'),
                    'org': result.get('org'),
                    'location': result.get('location')
                }

            return results['matches']
        except Exception as e:
            print(f"[!] Erro: {e}")
            return []

    def search_virustotal(self, ioc_value, ioc_type='domain'):
        """Busca VirusTotal."""
        if not self.vt_key:
            print("[!] VirusTotal API key não configurada")
            return {}

        print(f"\n🦠 VirusTotal: {ioc_value} ({ioc_type})")

        url = f"https://www.virustotal.com/api/v3/{ioc_type}s/{ioc_value}"
        headers = {'x-apikey': self.vt_key}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()['data']

                stats = data['attributes']['last_analysis_stats']
                print(f"  Malicious: {stats['malicious']}")
                print(f"  Suspicious: {stats['suspicious']}")
                print(f"  Undetected: {stats['undetected']}")

                self.results['virustotal'][ioc_value] = {
                    'malicious': stats['malicious'],
                    'suspicious': stats['suspicious'],
                    'undetected': stats['undetected'],
                    'type': ioc_type
                }

                return data
            else:
                print(f"[!] Resposta: {response.status_code}")
                return {}
        except Exception as e:
            print(f"[!] Erro: {e}")
            return {}

    def search_certificates(self, domain):
        """Busca certificados SSL (CT logs)."""
        print(f"\n📜 Certificate Transparency: {domain}")

        url = f"https://crt.sh/?q=%.{domain}&output=json"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                certs = response.json()

                subdomains = set()
                for cert in certs:
                    name = cert.get('name_value', '')
                    for sub in name.split('\n'):
                        sub = sub.strip()
                        if sub and sub.endswith(domain):
                            subdomains.add(sub)

                print(f"[+] {len(subdomains)} subdomínios únicos encontrados")

                for sub in sorted(list(subdomains))[:20]:
                    print(f"  • {sub}")
                    self.results['certificates'].append(sub)

                return list(subdomains)
            else:
                print(f"[!] Erro: {response.status_code}")
                return []
        except Exception as e:
            print(f"[!] Erro: {e}")
            return []

    def dns_enumeration(self, domain):
        """Enumeração DNS básica."""
        print(f"\n🔎 DNS Enumeration: {domain}")

        import dns.resolver

        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']

        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                print(f"  {record_type}: ", end='')

                values = []
                for rdata in answers:
                    values.append(str(rdata))
                    print(str(rdata), end=' ')

                self.results['dns'][record_type] = values
                print()
            except:
                pass

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'shodan_results': len(self.results['shodan']),
                'vt_results': len(self.results['virustotal']),
                'certificates': len(self.results['certificates']),
                'dns_records': len(self.results['dns'])
            },
            'details': self.results
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n[+] Relatório: {output_file}")

        print(f"\n{'='*50}")
        print(f"📊 RESUMO")
        print(f"{'='*50}")
        for key, value in report['summary'].items():
            print(f"{key}: {value}")

        return report

def main():
    import os

    parser = argparse.ArgumentParser(description="OSINT API Wrapper")
    parser.add_argument('--shodan', help='Busca Shodan')
    parser.add_argument('--virustotal', help='Busca VirusTotal')
    parser.add_argument('--domains', help='Extrai domínios (CT logs)')
    parser.add_argument('--dns', help='Enumeração DNS')
    parser.add_argument('--full-recon', help='Recon completo')
    parser.add_argument('-o', '--output', help='Arquivo JSON')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔍 OSINT API Wrapper")
    print(f"{'='*70}\n")

    osint = OSINTWrapper()

    if args.full_recon:
        target = args.full_recon
        osint.results['target'] = target
        osint.search_shodan(target)
        osint.search_virustotal(target, 'domain')
        osint.search_certificates(target)
        osint.dns_enumeration(target)
    else:
        if args.shodan:
            osint.search_shodan(args.shodan)
        if args.virustotal:
            osint.search_virustotal(args.virustotal)
        if args.domains:
            osint.search_certificates(args.domains)
        if args.dns:
            osint.dns_enumeration(args.dns)

    osint.generate_report(args.output)
    print("\n[✓] OSINT completo!")

if __name__ == "__main__":
    import os
    main()
