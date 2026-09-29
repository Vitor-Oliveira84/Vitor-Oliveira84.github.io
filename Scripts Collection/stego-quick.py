#!/usr/bin/env python3
"""Stego Quick Check - Testa esteganografia rapidamente sem ser caro.

Uso:
  python stego-quick.py <imagem>              # Verificação rápida
  python stego-quick.py <imagem> --lsb-check  # Testa LSB (mais lento)
  python stego-quick.py <imagem> --planes     # Extrai planos de bits
  python stego-quick.py <diretório> --batch   # Processa múltiplas imagens

Estratégia:
  1. Dados após IEND (PNG) / FFD9 (JPEG) - RÁPIDO
  2. Chunks/segmentos especiais - RÁPIDO
  3. Planos de bits (visual) - MÉDIO
  4. LSB (pixel-level) - LENTO (só se necessário)
"""
import os
import sys
import struct
import re
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
    HAS_PIL = True
except:
    HAS_PIL = False
    print("⚠️  Pillow/numpy não instalado (LSB): pip install pillow numpy")

class StegoQuickCheck:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.findings = []

    def check(self, filepath):
        """Verificação rápida de esteganografia."""
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return

        try:
            with open(filepath, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"❌ Erro ao ler {filepath}: {e}")
            return

        print(f"\n{'='*70}")
        print(f"🔍 Verificando: {os.path.basename(filepath)}")
        print(f"{'='*70}\n")

        # Detecta tipo
        if data.startswith(b'\x89PNG'):
            self._check_png(filepath, data)
        elif data.startswith(b'\xff\xd8'):
            self._check_jpeg(filepath, data)
        else:
            print(f"⚠️  Tipo não suportado (magic: {data[:4].hex()})")

    def _check_png(self, filepath, data):
        """Verifica PNG para esteganografia."""
        print(f"📊 Analisando PNG...\n")

        # 1. Chunks especiais
        print(f"1️⃣  CHUNKS ESPECIAIS:")
        o = 8
        found_chunks = False
        while o + 8 <= len(data):
            l = struct.unpack(">I", data[o:o+4])[0]
            t = data[o+4:o+8].decode("ascii", "replace")

            if t in ("tEXt", "iTXt", "zTXt", "eXIf", "COM", "IEND"):
                found_chunks = True
                chunk_data = data[o+8:o+8+l]
                print(f"   • {t}: {l} bytes")

                # Procura por padrões
                if b'flag' in chunk_data.lower() or b'FirstFlag' in chunk_data:
                    print(f"     ⚠️  FLAG PATTERN ENCONTRADO!")
                    self.findings.append((filepath, "chunk_flag", chunk_data[:100]))

                if re.search(rb'[\x20-\x7e]{10,}', chunk_data):
                    print(f"     📝 Contém texto ASCII")

            o += 12 + l
            if t == "IEND":
                iend_pos = o - 12 - l
                break

        if not found_chunks:
            print(f"   ⚠️  Nenhum chunk especial")

        # 2. Dados após IEND
        print(f"\n2️⃣  DADOS APÓS IEND:")
        if len(data) > iend_pos + 8:
            extra = data[iend_pos+8:]
            print(f"   ⚠️  {len(extra)} bytes após IEND!")
            if len(extra) > 0:
                print(f"   Primeiros 100 bytes: {extra[:100]!r}")
                self.findings.append((filepath, "extra_data_after_iend", extra))
        else:
            print(f"   ✅ Nenhum dado após IEND")

        # 3. Planos de bits (visual)
        if '--planes' in sys.argv and HAS_PIL:
            self._extract_planes(filepath)

        # 4. LSB (lento)
        if '--lsb-check' in sys.argv and HAS_PIL:
            self._check_lsb(filepath)

    def _check_jpeg(self, filepath, data):
        """Verifica JPEG para esteganografia."""
        print(f"📊 Analisando JPEG...\n")

        # 1. Segmentos especiais
        print(f"1️⃣  SEGMENTOS ESPECIAIS:")
        o = 2
        found_special = False
        while o < len(data) and data[o] == 0xFF:
            m = data[o+1]
            if m == 0xDA:
                break

            l = struct.unpack(">H", data[o+2:o+4])[0]
            body = data[o+4:o+2+l]

            tag = {0xFE: "COM", 0xE1: "EXIF", 0xE2: "ICC", 0xE8: "SPIFF"}.get(m, f"APP{m&0x0f}")

            if m in (0xFE, 0xE1, 0xE2):
                found_special = True
                print(f"   • {tag} ({m:#x}): {l} bytes")

                # Tenta decodificar como hex/base64
                if b'0x' in body[:20] or b'-----BEGIN' in body[:30]:
                    print(f"     📌 Pode conter dados codificados!")
                    self.findings.append((filepath, f"segment_{tag}", body[:100]))

            o += 2 + l

        if not found_special:
            print(f"   ⚠️  Nenhum segmento especial (apenas padrão)")

        # 2. Dados após FFD9 (EOI)
        print(f"\n2️⃣  DADOS APÓS EOI (FFD9):")
        eoi_pos = data.rfind(b'\xff\xd9')
        if eoi_pos > 0 and eoi_pos + 2 < len(data):
            extra = data[eoi_pos+2:]
            print(f"   ⚠️  {len(extra)} bytes após FFD9!")
            print(f"   Primeiros 100 bytes: {extra[:100]!r}")
            self.findings.append((filepath, "extra_data_after_eoi", extra))
        else:
            print(f"   ✅ Nenhum dado após FFD9")

        # 3. Planos de bits
        if '--planes' in sys.argv and HAS_PIL:
            self._extract_planes(filepath)

        # 4. LSB
        if '--lsb-check' in sys.argv and HAS_PIL:
            self._check_lsb(filepath)

    def _extract_planes(self, filepath):
        """Extrai planos de bits para análise visual."""
        if not HAS_PIL:
            print(f"\n⚠️  PIL não instalado")
            return

        print(f"\n3️⃣  PLANOS DE BITS:")
        try:
            img = Image.open(filepath).convert('RGB')
            arr = np.array(img)

            # Extrai LSBs de cada canal
            for c, name in enumerate(['R', 'G', 'B']):
                lsbs = arr[:, :, c] & 1
                entropy = -np.sum(np.bincount(lsbs.flatten()) / lsbs.size *
                                 np.log2(np.bincount(lsbs.flatten()) / lsbs.size + 1e-10))

                print(f"   • Canal {name} LSB: entropia {entropy:.2f}", end="")
                if entropy > 0.9:
                    print(f" ⚠️  ESTRUTURA DETECTADA (pode conter dados)")
                else:
                    print(f" ✅ Aleatório (sem esteganografia óbvia)")

            # Salva imagem de planos
            tiles = [((arr[:, :, c] >> b) & 1) * 255
                    for c in range(3) for b in (0, 1, 2)]
            rows = [np.hstack(tiles[i*3:i*3+3]) for i in range(3)]
            out = filepath.replace('.jpg', '_planes.png').replace('.png', '_planes.png')
            Image.fromarray(np.vstack(rows).astype('uint8')).save(out)
            print(f"   💾 Planos salvos em: {out}")
            print(f"      Abra e procure por formas/padrões nos 9 blocos")

        except Exception as e:
            print(f"   ❌ Erro ao extrair planos: {e}")

    def _check_lsb(self, filepath):
        """Verifica LSB (lento)."""
        if not HAS_PIL:
            return

        print(f"\n4️⃣  VERIFICAÇÃO LSB (lento):")
        try:
            img = Image.open(filepath).convert('RGBA')
            arr = np.array(img)

            # Extrai LSBs
            lsbs = arr[:, :, :3] & 1
            bits = lsbs.reshape(-1)
            data = np.packbits(bits).tobytes()

            print(f"   📊 {len(data)} bytes extraídos")

            # Procura por padrões
            if b'flag' in data.lower() or b'FirstFlag' in data:
                print(f"   ⚠️  FLAG PATTERN ENCONTRADO EM LSB!")
                self.findings.append((filepath, "lsb_flag", data[:100]))
            else:
                print(f"   ✅ Nenhum padrão de flag em LSB")

        except Exception as e:
            print(f"   ❌ Erro: {e}")

    def report(self):
        """Relatório final."""
        if self.findings:
            print(f"\n{'='*70}")
            print(f"⚠️  ACHADOS DE ESTEGANOGRAFIA:")
            print(f"{'='*70}")
            for filepath, finding_type, data in self.findings:
                print(f"\n📁 {os.path.basename(filepath)}")
                print(f"   Tipo: {finding_type}")
                print(f"   Dados: {data[:100]!r}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    filepath = sys.argv[1]
    batch = '--batch' in sys.argv

    checker = StegoQuickCheck()

    if batch and os.path.isdir(filepath):
        print(f"🔄 Modo batch: verificando {filepath}...")
        for f in Path(filepath).glob('**/*'):
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                checker.check(str(f))
    else:
        checker.check(filepath)

    checker.report()

if __name__ == "__main__":
    main()
