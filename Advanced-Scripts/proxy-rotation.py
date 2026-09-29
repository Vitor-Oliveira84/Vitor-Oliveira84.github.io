#!/usr/bin/env python3
"""Proxy Auto-Rotation - Rotação automática de proxies para OSINT

Uso:
  python proxy-rotation.py -u http://target.com --proxies proxies.txt
  python proxy-rotation.py -l urls.txt --threads 10
"""
import requests
import time
from itertools import cycle

class ProxyRotator:
    def __init__(self, proxy_list):
        self.proxies = cycle(proxy_list)
        self.current_proxy = None

    def get_next_proxy(self):
        self.current_proxy = next(self.proxies)
        return {'http': self.current_proxy, 'https': self.current_proxy}

    def test_url(self, url, timeout=5):
        try:
            proxy = self.get_next_proxy()
            response = requests.get(url, proxies=proxy, timeout=timeout, verify=False)
            print(f"[✓] {url} via {self.current_proxy}: {response.status_code}")
            return response
        except Exception as e:
            print(f"[!] Erro com {self.current_proxy}: {e}")
            return None

# Uso básico
if __name__ == "__main__":
    proxies = ['http://proxy1:8080', 'http://proxy2:8080']
    rotator = ProxyRotator(proxies)

    for url in ['http://example.com']:
        rotator.test_url(url)
