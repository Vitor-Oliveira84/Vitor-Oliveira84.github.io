#!/usr/bin/env python3
"""Decoder Multi-Formato - Testa múltiplos tipos de decodificação em paralelo.

Uso:
  python decoder-parallel.py <texto>              # Testa todos os formatos
  python decoder-parallel.py <texto> --smart      # Detecta automaticamente tipo
  python decoder-parallel.py <arquivo> --file     # Lê de arquivo
  python decoder-parallel.py <texto> --all-caesar # Mostra todos os 26 Caesar
"""
import sys
import base64
import binascii
import codecs
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

KEYWORDS = [
    'flag', 'FLAG', 'FirstFlag', 'password', 'passwd', 'admin', 'secret',
    'key', 'ctf', 'CTF', 'auth', 'login', 'token', 'academy', 'THM', 'HTB'
]

class DecoderParallel:
    def __init__(self):
        self.results = {}
        self.found_keywords = []

    def _contains_keyword(self, text):
        """Verifica se contém palavras-chave."""
        if isinstance(text, bytes):
            text_str = text.decode(errors='replace')
        else:
            text_str = str(text)

        for kw in KEYWORDS:
            if kw.lower() in text_str.lower():
                self.found_keywords.append((kw, text_str[:100]))
                return True
        return False

    def _try_hex(self, text):
        """Tenta decodificar de hexadecimal."""
        try:
            decoded = binascii.unhexlify(text.strip())
            return ('hex', decoded)
        except:
            return None

    def _try_base64(self, text):
        """Tenta decodificar de Base64."""
        try:
            # Base64 válido termina com = ou ==
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', text.strip()):
                return None
            decoded = base64.b64decode(text.strip(), validate=True)
            return ('base64', decoded)
        except:
            return None

    def _try_base32(self, text):
        """Tenta decodificar de Base32."""
        try:
            decoded = base64.b32decode(text.strip())
            return ('base32', decoded)
        except:
            return None

    def _try_rot13(self, text):
        """ROT13."""
        try:
            decoded = codecs.encode(text, 'rot_13')
            return ('rot13', decoded)
        except:
            return None

    def _try_caesar(self, text, shift):
        """Caesar cipher com deslocamento específico."""
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        return ''.join(result)

    def _all_caesar(self, text):
        """Testa todos os 26 deslocamentos Caesar."""
        results = []
        for k in range(1, 26):
            decoded = self._try_caesar(text, -k)
            results.append((f'caesar-{k}', decoded))
        return results

    def _try_url_decode(self, text):
        """URL decode."""
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(text)
            if decoded != text:
                return ('url', decoded)
        except:
            pass
        return None

    def _try_unicode_escape(self, text):
        """Unicode escape."""
        try:
            decoded = text.encode().decode('unicode_escape')
            if decoded != text:
                return ('unicode_escape', decoded)
        except:
            pass
        return None

    def decode_all(self, text, all_caesar=False):
        """Executa todos os decoders em paralelo."""
        decoders = [
            (self._try_hex, text),
            (self._try_base64, text),
            (self._try_base32, text),
            (self._try_rot13, text),
            (self._try_url_decode, text),
            (self._try_unicode_escape, text),
        ]

        print(f"\n{'='*70}")
        print(f"🔐 Testando múltiplas codificações...")
        print(f"{'='*70}\n")

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(decoder, arg): name
                for decoder, arg in decoders
                for name in [decoder.__name__]
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        fmt, decoded = result
                        self._print_result(fmt, decoded)
                except Exception as e:
                    pass

        # Caesar cipher
        print(f"\n🔤 CAESAR CIPHER (todos os 26 deslocamentos):\n")
        for fmt, decoded in self._all_caesar(text):
            if self._contains_keyword(decoded):
                mark = "  ✅ <== PALAVRA-CHAVE ENCONTRADA"
            else:
                mark = ""
            print(f"  {fmt}: {decoded[:70]}{mark}")

        # Resultado final
        if self.found_keywords:
            print(f"\n{'='*70}")
            print(f"✅ PALAVRAS-CHAVE ENCONTRADAS:")
            for kw, text in self.found_keywords:
                print(f"   • '{kw}' em: {text}")

    def _print_result(self, fmt, decoded):
        """Formata e imprime resultado."""
        if isinstance(decoded, bytes):
            try:
                text_str = decoded.decode('utf-8')
                keyword_mark = " ✅ PALAVRA-CHAVE" if self._contains_keyword(text_str) else ""
                print(f"✅ [{fmt:15}] {text_str[:80]}{keyword_mark}")
            except:
                print(f"⚠️  [{fmt:15}] (bytes não-UTF8): {decoded[:60].hex()}")
        else:
            keyword_mark = " ✅ PALAVRA-CHAVE" if self._contains_keyword(decoded) else ""
            print(f"✅ [{fmt:15}] {decoded[:80]}{keyword_mark}")

def smart_detect(text):
    """Detecta automaticamente o tipo de codificação."""
    if re.match(r'^[0-9a-fA-F]+$', text.strip()) and len(text) % 2 == 0:
        return 'hex'
    elif re.match(r'^[A-Za-z0-9+/]*={0,2}$', text.strip()):
        return 'base64'
    elif re.match(r'^[A-Z2-7]+=*$', text.strip()):
        return 'base32'
    elif '%' in text:
        return 'url'
    else:
        return 'caesar'

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    text = sys.argv[1]
    all_caesar = '--all-caesar' in sys.argv
    smart = '--smart' in sys.argv
    use_file = '--file' in sys.argv

    if use_file:
        try:
            with open(text, 'r') as f:
                text = f.read().strip()
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return

    decoder = DecoderParallel()

    if smart:
        detected = smart_detect(text)
        print(f"🔍 Tipo detectado: {detected}")
        print(f"    Dica: se errado, execute sem --smart\n")

    decoder.decode_all(text, all_caesar=all_caesar)

if __name__ == "__main__":
    main()
