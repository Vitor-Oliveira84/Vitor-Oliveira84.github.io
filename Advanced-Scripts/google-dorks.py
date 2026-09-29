#!/usr/bin/env python3
"""Google Dorks Automation - Busca automática de informações sensíveis

Uso:
  python google-dorks.py -d example.com --exposed-files
  python google-dorks.py -d example.com --api-keys
  python google-dorks.py -d example.com --backup-files
  python google-dorks.py -d example.com --admin-panels
  python google-dorks.py -d example.com --all

Dorks incluídos:
  - Arquivos expostos (backup, config)
  - API keys
  - Painel admin
  - Arquivos de log
  - Credentials
  - Código-fonte
"""
import sys
import argparse
import json
import time
import requests
from urllib.parse import quote

class GoogleDorker:
    def __init__(self, delay=1):
        self.delay = delay
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })

    def search_dork(self, domain, dork_query):
        """Executa busca de dork."""
        search_query = f"site:{domain} {dork_query}"

        try:
            # Nota: Google bloqueia bots, esta é uma versão educacional
            url = f"https://www.google.com/search?q={quote(search_query)}&num=100"

            response = self.session.get(url, timeout=10, verify=False)

            # Verificar captcha/bloqueio
            if 'unusual traffic' in response.text.lower():
                print(f"  [!] Google detectou bot - aguardando...")
                time.sleep(30)
                return []

            # Parse básico
            results = []
            if 'No results found' not in response.text:
                print(f"  ✓ Resultados encontrados")

            time.sleep(self.delay)
            return results

        except Exception as e:
            print(f"  [!] Erro: {e}")
            return []

    def search_dorks_by_category(self, domain, category):
        """Busca dorks por categoria."""

        dorks = {
            'exposed_files': [
                'filetype:bak',
                'filetype:config',
                'filetype:sql',
                'filetype:log',
                'filetype:conf',
                '".env" OR ".env.local"',
                '"config.php"',
                '"wp-config.php"',
                '"database.yml"',
                '"secrets.json"'
            ],
            'api_keys': [
                'inurl:api',
                '"api_key"',
                '"apikey"',
                '"API_KEY"',
                '"secret"',
                '"PASSWORD"',
                '"authorization: Bearer"',
                'inurl:token'
            ],
            'backup_files': [
                'filetype:zip OR filetype:rar',
                'filetype:tar OR filetype:gz',
                '".backup"',
                '".old"',
                '".bak"',
                '".sql.gz"'
            ],
            'admin_panels': [
                'inurl:admin',
                'inurl:administrator',
                'inurl:wp-admin',
                'inurl:login',
                'inurl:dashboard',
                'inurl:panel'
            ],
            'credentials': [
                '"username:" OR "password:"',
                '"login:" "pass:"',
                'inurl:password OR inurl:passwd',
                '"email" "password"'
            ],
            'source_code': [
                'filetype:github',
                'filetype:gitlab',
                'inurl:raw',
                'inurl:code'
            ],
            'logs': [
                'filetype:log',
                'inurl:logs',
                'error.log',
                'access.log'
            ]
        }

        if category not in dorks:
            print(f"[!] Categoria desconhecida: {category}")
            return

        print(f"\n🔍 Buscando {category}...")
        results = []

        for dork in dorks[category]:
            print(f"  Testando: {dork}")
            dork_results = self.search_dork(domain, dork)
            results.extend(dork_results)

        self.results[category] = results
        return results

    def search_all_categories(self, domain):
        """Busca todas as categorias."""
        categories = [
            'exposed_files',
            'api_keys',
            'backup_files',
            'admin_panels',
            'credentials',
            'source_code',
            'logs'
        ]

        for cat in categories:
            self.search_dorks_by_category(domain, cat)
            time.sleep(self.delay)

    def generate_report(self, domain, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'domain': domain,
            'summary': {k: len(v) for k, v in self.results.items()},
            'results': self.results
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n[+] Relatório: {output_file}")

        print(f"\n{'='*50}")
        print(f"📊 RESUMO")
        print(f"{'='*50}")
        for category, count in report['summary'].items():
            print(f"{category}: {count}")

        return report

def main():
    parser = argparse.ArgumentParser(description="Google Dorks Automation")
    parser.add_argument('-d', '--domain', required=True, help='Domínio alvo')
    parser.add_argument('--exposed-files', action='store_true')
    parser.add_argument('--api-keys', action='store_true')
    parser.add_argument('--backup-files', action='store_true')
    parser.add_argument('--admin-panels', action='store_true')
    parser.add_argument('--credentials', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('-o', '--output', help='Arquivo JSON')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔍 Google Dorks - {args.domain}")
    print(f"{'='*70}\n")

    dorker = GoogleDorker()

    if args.all:
        dorker.search_all_categories(args.domain)
    else:
        if args.exposed_files:
            dorker.search_dorks_by_category(args.domain, 'exposed_files')
        if args.api_keys:
            dorker.search_dorks_by_category(args.domain, 'api_keys')
        if args.backup_files:
            dorker.search_dorks_by_category(args.domain, 'backup_files')
        if args.admin_panels:
            dorker.search_dorks_by_category(args.domain, 'admin_panels')
        if args.credentials:
            dorker.search_dorks_by_category(args.domain, 'credentials')

    dorker.generate_report(args.domain, args.output)
    print("\n[✓] Busca completada!")

if __name__ == "__main__":
    main()
