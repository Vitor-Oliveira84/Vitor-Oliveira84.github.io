#!/usr/bin/env python3
"""Token Leakage Scanner - Detecta vazamento de tokens sensíveis

Uso:
  python token-leakage-scanner.py -a "http://api" --scan-responses
  python token-leakage-scanner.py -a "http://api" --test-patterns

CLLMSE Topics: Token Leakage, API Security, Data Exposure
"""
import requests
import re
import json

class TokenLeakageScanner:
    def __init__(self, api_url):
        self.api_url = api_url
        self.results = {'tokens_found': [], 'patterns_detected': []}

        # Padrões de tokens conhecidos
        self.token_patterns = {
            'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})',
            'bearer_token': r'bearer\s+([a-zA-Z0-9\-_\.]{20,})',
            'jwt': r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'ghp_[a-zA-Z0-9_]{36}',
            'slack_token': r'xox[bap]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24,32}',
            'private_key': r'-----BEGIN (RSA|OPENSSH|EC)? PRIVATE KEY',
            'password': r'password["\']?\s*[:=]\s*["\']?([^"\']{8,})',
            'database_uri': r'(mysql|postgres|mongodb)://[^\s"\']+',
        }

    def scan_for_tokens(self, text):
        """Scana texto procurando por tokens"""
        found_tokens = []

        for token_type, pattern in self.token_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found_tokens.append({
                    'type': token_type,
                    'value': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0)
                })

        return found_tokens

    def test_error_messages(self):
        """Testa se mensagens de erro revelam tokens"""
        error_triggers = [
            "undefined variable",
            "throw new Error('test')",
            "raise Exception('test')",
            "SELECT * FROM users WHERE id = 'test'",
        ]

        leaked = []

        for trigger in error_triggers:
            try:
                data = {'messages': [{'role': 'user', 'content': trigger}], 'model': 'gpt-3.5'}
                response = requests.post(self.api_url, json=data, timeout=10, verify=False)

                if response.status_code == 200:
                    tokens = self.scan_for_tokens(response.text)
                    if tokens:
                        leaked.extend(tokens)
            except:
                pass

        return leaked

    def test_response_headers(self):
        """Verifica headers de resposta para tokens"""
        try:
            response = requests.get(self.api_url, timeout=10, verify=False)

            sensitive_headers = [
                'Authorization',
                'X-API-Key',
                'X-Auth-Token',
                'Cookie',
                'Set-Cookie'
            ]

            leaked = []
            for header in sensitive_headers:
                if header in response.headers:
                    value = response.headers[header][:30]
                    leaked.append({
                        'location': 'HTTP Header',
                        'header': header,
                        'value': value
                    })

            return leaked
        except:
            return []

    def test_verbose_errors(self):
        """Testa se erros são verbose e revelam informações"""
        tests = [
            "SELECT * FROM",
            "import os; os.system",
            "<?php system",
        ]

        verbose_errors = []

        for test in tests:
            try:
                data = {'messages': [{'role': 'user', 'content': test}], 'model': 'gpt-3.5'}
                response = requests.post(self.api_url, json=data, timeout=10, verify=False)

                if response.status_code == 200:
                    content = response.text

                    # Verifica se há detalhes demais
                    if any(x in content.lower() for x in ['traceback', 'stack', 'error:', 'exception']):
                        verbose_errors.append({'trigger': test, 'verbose': True})
            except:
                pass

        return verbose_errors

    def run_assessment(self):
        """Executa avaliação de vazamento de tokens"""
        print(f"\n[*] Token Leakage Scanner")
        print(f"[*] API: {self.api_url}\n")

        # Testa mensagens de erro
        print(f"[1/3] Testing error messages...")
        error_tokens = self.test_error_messages()
        if error_tokens:
            print(f"  [!] {len(error_tokens)} tokens found in error messages")
            self.results['tokens_found'].extend(error_tokens)

        # Testa headers
        print(f"[2/3] Testing HTTP headers...")
        header_tokens = self.test_response_headers()
        if header_tokens:
            print(f"  [!] {len(header_tokens)} sensitive headers exposed")
            self.results['tokens_found'].extend(header_tokens)

        # Testa erros verbose
        print(f"[3/3] Testing verbose error messages...")
        verbose = self.test_verbose_errors()
        if verbose:
            print(f"  [!] {len(verbose)} verbose error patterns detected")

    def generate_report(self):
        """Gera relatório"""
        print(f"\n{'='*70}")
        print(f"📊 TOKEN LEAKAGE SCAN REPORT")
        print(f"{'='*70}")
        print(f"Tokens found: {len(self.results['tokens_found'])}")

        if self.results['tokens_found']:
            print(f"\n[!] SENSITIVE TOKENS DETECTED:")
            for token in self.results['tokens_found']:
                print(f"  • {token}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Token Leakage Scanner")
    parser.add_argument('-a', '--api', required=True, help='API URL')
    parser.add_argument('--scan-responses', action='store_true')
    parser.add_argument('--test-patterns', action='store_true')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔑 Token Leakage Scanner - CLLMSE Assessment")
    print(f"{'='*70}")

    scanner = TokenLeakageScanner(args.api)
    scanner.run_assessment()
    scanner.generate_report()

if __name__ == "__main__":
    main()
