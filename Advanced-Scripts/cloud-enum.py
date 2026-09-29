#!/usr/bin/env python3
"""Cloud Enumeration - AWS, Azure, GCP metadata extraction

Uso:
  python cloud-enum.py --aws
  python cloud-enum.py --azure
  python cloud-enum.py --all
"""
import requests

class CloudEnum:
    def enum_aws(self):
        """Extrai metadata AWS"""
        url = "http://169.254.169.254/latest/meta-data/"
        try:
            response = requests.get(url, timeout=2)
            print(f"[+] AWS Metadata encontrado!")
            print(response.text)
        except:
            print("[-] AWS Metadata não acessível")

    def enum_azure(self):
        """Extrai metadata Azure"""
        url = "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
        headers = {"Metadata": "true"}
        try:
            response = requests.get(url, headers=headers, timeout=2)
            print(f"[+] Azure Metadata encontrado!")
            print(response.json())
        except:
            print("[-] Azure Metadata não acessível")

    def enum_gcp(self):
        """Extrai metadata GCP"""
        url = "http://metadata.google.internal/computeMetadata/v1/"
        headers = {"Metadata-Flavor": "Google"}
        try:
            response = requests.get(url, headers=headers, timeout=2)
            print(f"[+] GCP Metadata encontrado!")
            print(response.text)
        except:
            print("[-] GCP Metadata não acessível")

if __name__ == "__main__":
    enum = CloudEnum()
    enum.enum_aws()
    enum.enum_azure()
    enum.enum_gcp()
