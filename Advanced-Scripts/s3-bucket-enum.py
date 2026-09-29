#!/usr/bin/env python3
"""S3 Bucket Enumeration - Detecta e explora buckets AWS S3 mal configurados.

Uso:
  python s3-bucket-enum.py -d example.com
  python s3-bucket-enum.py -b mybucket
  python s3-bucket-enum.py -d example.com --fuzzing
  python s3-bucket-enum.py -d example.com --download
  python s3-bucket-enum.py -l buckets.txt --batch

Dependências:
  pip install boto3 requests

Técnicas:
  - Descoberta por DNS
  - Fuzzing de nomes
  - Teste de ACL
  - Dump de conteúdo
"""
import sys
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import boto3
    import botocore
    import requests
except ImportError:
    print("❌ Dependências: pip install boto3 requests")
    sys.exit(1)

class S3Enumerator:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.results = {
            'buckets_found': [],
            'accessible': [],
            'misconfigured': [],
            'contents': []
        }

    def check_bucket_exists(self, bucket_name):
        """Verifica se bucket existe (sem credenciais)."""
        try:
            # HEAD request para verificar existência
            response = requests.head(f"https://{bucket_name}.s3.amazonaws.com/", timeout=5)
            if response.status_code != 404:
                return True
        except:
            pass

        # Tenta via boto3 (sem credenciais)
        try:
            s3 = boto3.client('s3', region_name=self.region)
            s3.head_bucket(Bucket=bucket_name)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            # 403 = exists but not accessible without auth
            return True
        except:
            return False

    def check_bucket_permissions(self, bucket_name):
        """Verifica permissões do bucket."""
        results = {
            'bucket': bucket_name,
            'exists': False,
            'public': False,
            'listable': False,
            'writable': False,
            'acl': None,
            'policy': None
        }

        try:
            s3 = boto3.client('s3', region_name=self.region)

            # Verifica existência
            s3.head_bucket(Bucket=bucket_name)
            results['exists'] = True

            # Tenta listar conteúdo (anonymous)
            try:
                s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                results['listable'] = True
                print(f"  🔓 LISTÁVEL: {bucket_name}")
            except:
                pass

            # Tenta ler ACL
            try:
                acl = s3.get_bucket_acl(Bucket=bucket_name)
                results['acl'] = "PublicRead" if any(
                    g.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                    for g in acl.get('Grants', [])
                ) else "Private"
                if results['acl'] == "PublicRead":
                    results['public'] = True
                    print(f"  📤 PÚBLICO: {bucket_name}")
            except:
                pass

            # Tenta ler policy
            try:
                policy = s3.get_bucket_policy(Bucket=bucket_name)
                results['policy'] = policy['Policy']
                print(f"  📋 POLICY ENCONTRADA: {bucket_name}")
            except:
                pass

            # Tenta upload (write test)
            try:
                s3.put_object(Bucket=bucket_name, Key='.write-test', Body=b'test')
                results['writable'] = True
                print(f"  ✏️  GRAVÁVEL: {bucket_name}")
                # Cleanup
                s3.delete_object(Bucket=bucket_name, Key='.write-test')
            except:
                pass

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                results['exists'] = True
        except Exception as e:
            pass

        return results

    def enumerate_bucket_contents(self, bucket_name, max_items=100):
        """Lista conteúdo do bucket (se acessível)."""
        contents = []
        try:
            s3 = boto3.client('s3', region_name=self.region)
            paginator = s3.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=bucket_name, PaginationConfig={'PageSize': 100}):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        contents.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': str(obj['LastModified']),
                            'storage_class': obj['StorageClass']
                        })

                        if len(contents) >= max_items:
                            break
                if len(contents) >= max_items:
                    break

            print(f"  📦 {len(contents)} objetos listados")
        except Exception as e:
            pass

        return contents

    def fuzz_bucket_names(self, domain):
        """Fuzz de nomes de bucket."""
        patterns = [
            f"{domain}",
            f"{domain}-backup",
            f"{domain}-staging",
            f"{domain}-dev",
            f"{domain}-prod",
            f"{domain}-data",
            f"{domain}-uploads",
            f"{domain}-logs",
            f"{domain}-assets",
            f"backup-{domain}",
            f"test-{domain}",
            f"staging-{domain}",
        ]

        buckets = []
        print(f"\n🔍 Fuzzando nomes de bucket...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.check_bucket_exists, name): name for name in patterns}

            for future in as_completed(futures):
                bucket = futures[future]
                try:
                    if future.result():
                        buckets.append(bucket)
                        print(f"  ✅ Encontrado: {bucket}")
                except:
                    pass

        return buckets

    def generate_report(self, output_file=None):
        """Gera relatório."""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_buckets': len(self.results['buckets_found']),
                'accessible': len(self.results['accessible']),
                'misconfigured': len(self.results['misconfigured']),
            },
            'details': self.results
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Relatório: {output_file}")

        return report

def main():
    parser = argparse.ArgumentParser(description="S3 Bucket Enumeration")
    parser.add_argument('-d', '--domain', help='Domínio alvo')
    parser.add_argument('-b', '--bucket', help='Bucket específico')
    parser.add_argument('-l', '--list', help='Lista de buckets')
    parser.add_argument('--fuzzing', action='store_true', help='Fuzz de nomes')
    parser.add_argument('--download', action='store_true', help='Baixa objetos')
    parser.add_argument('--batch', action='store_true', help='Processa lote')
    parser.add_argument('-o', '--output', help='Arquivo de saída')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"🪣 S3 Bucket Enumeration")
    print(f"{'='*70}\n")

    enum = S3Enumerator()

    buckets_to_check = []

    if args.bucket:
        buckets_to_check = [args.bucket]
    elif args.domain:
        if args.fuzzing:
            buckets_to_check = enum.fuzz_bucket_names(args.domain)
        else:
            buckets_to_check = [args.domain]
    elif args.list:
        with open(args.list) as f:
            buckets_to_check = [line.strip() for line in f if line.strip()]

    # Verificar permissões
    print(f"\n🔍 Verificando {len(buckets_to_check)} bucket(s)...")
    for bucket in buckets_to_check:
        result = enum.check_bucket_permissions(bucket)
        enum.results['buckets_found'].append(result)

        if result['exists']:
            enum.results['accessible'].append(result)
            if result['public'] or result['listable'] or result['writable']:
                enum.results['misconfigured'].append(result)

                # Enumera conteúdo se acessível
                if result['listable'] and args.download:
                    contents = enum.enumerate_bucket_contents(bucket)
                    enum.results['contents'].extend(contents)

    # Report
    enum.generate_report(args.output or f"s3_buckets_{int(time.time())}.json")

    print(f"\n✅ Enumeração completa!")

if __name__ == "__main__":
    main()
