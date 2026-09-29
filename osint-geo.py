#!/usr/bin/env python3
"""OSINT + Geolocalização - Análise de metadados e busca de informações.

Uso:
  python osint-geo.py <imagem.jpg>              # Análise EXIF completa
  python osint-geo.py <imagem> --ocr            # OCR de placas/texto (requer pytesseract)
  python osint-geo.py <imagem> --gps            # Apenas dados GPS
  python osint-geo.py <imagem> --verbose        # Detalhado com hints
  python osint-geo.py <diretório> --batch       # Processa múltiplas imagens

Dependências:
  pip install pillow piexif
  pip install pytesseract (opcional, requer Tesseract instalado)
"""
import os
import sys
import json
from pathlib import Path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except:
    print("❌ Pillow não instalado: pip install pillow")
    sys.exit(1)

try:
    import piexif
except:
    print("⚠️  piexif não instalado (GPS): pip install piexif")

try:
    import pytesseract
    HAS_OCR = True
except:
    HAS_OCR = False

class OSINTGeo:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.findings = []

    def analyze(self, filepath):
        """Análise completa de imagem."""
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return

        print(f"\n{'='*70}")
        print(f"🔍 Analisando: {os.path.basename(filepath)}")
        print(f"{'='*70}\n")

        try:
            img = Image.open(filepath)

            # Informações básicas
            print(f"📐 Dimensões: {img.width} x {img.height} px")
            print(f"📷 Formato: {img.format}")
            print(f"🎨 Modo: {img.mode}")

            # EXIF data
            self._extract_exif(filepath)

            # GPS
            self._extract_gps(filepath)

            # OCR (opcional)
            if HAS_OCR and '--ocr' in sys.argv:
                self._extract_text(img)

            # Análise visual (hints)
            if self.verbose:
                self._visual_hints(img)

        except Exception as e:
            print(f"❌ Erro ao analisar: {e}")

    def _extract_exif(self, filepath):
        """Extrai dados EXIF."""
        print(f"\n📊 EXIF DATA:")
        try:
            img = Image.open(filepath)
            exif_data = img._getexif() if hasattr(img, '_getexif') else None

            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, f"Tag {tag_id}")
                    print(f"  • {tag_name}: {str(value)[:100]}")
                    self.findings.append((tag_name, value))
            else:
                print("  ⚠️  Nenhum EXIF data encontrado")
        except Exception as e:
            print(f"  ❌ Erro ao ler EXIF: {e}")

    def _extract_gps(self, filepath):
        """Extrai dados GPS."""
        print(f"\n🗺️  GPS DATA:")
        try:
            exif_dict = piexif.load(filepath)

            if "GPS" in exif_dict:
                gps = exif_dict["GPS"]
                print(f"  ✅ Dados GPS encontrados!")

                # Latitude
                if piexif.ImageIFD.GPSInfo in exif_dict["0th"]:
                    lat = self._dms_to_decimal(gps.get(piexif.GPSIFD.GPSLatitude))
                    lon = self._dms_to_decimal(gps.get(piexif.GPSIFD.GPSLongitude))

                    if lat and lon:
                        print(f"  📍 Coordenadas: {lat:.6f}, {lon:.6f}")
                        print(f"  🔗 Google Maps: https://maps.google.com/?q={lat},{lon}")
                        self.findings.append(("GPS", f"{lat:.6f}, {lon:.6f}"))

                # Altitude
                alt = gps.get(piexif.GPSIFD.GPSAltitude)
                if alt:
                    alt_m = alt[0][0] / alt[0][1] if alt[0][1] != 0 else 0
                    print(f"  📏 Altitude: {alt_m:.1f}m")
            else:
                print("  ⚠️  Nenhum dado GPS encontrado")
        except Exception as e:
            print(f"  ⚠️  Erro ao ler GPS: {e}")

    def _extract_text(self, img):
        """OCR - Extrai texto visível (placas, letreiros)."""
        if not HAS_OCR:
            print("\n📝 OCR não disponível (pytesseract não instalado)")
            return

        print(f"\n📝 OCR - TEXTO DETECTADO:")
        try:
            text = pytesseract.image_to_string(img)
            if text.strip():
                for line in text.strip().split('\n'):
                    if line.strip():
                        print(f"  • {line}")
                        self.findings.append(("OCR", line))
            else:
                print("  ⚠️  Nenhum texto detectado")
        except Exception as e:
            print(f"  ❌ Erro no OCR: {e}")

    def _visual_hints(self, img):
        """Dicas para análise visual manual."""
        print(f"\n💡 HINTS PARA OSINT MANUAL:")
        print(f"  1. Procure por placas de rua, nomes de lojas, sinalizações")
        print(f"  2. Identifique estilo de arquitetura, clima, vegetação")
        print(f"  3. Observe lado da rua, semáforos, marcações de rodovia")
        print(f"  4. Anote badges, logos, números visíveis")
        print(f"  5. Procure no Google por: 'Wetherspoon [nome da placa]'")
        print(f"  6. Use Google Reverse Image Search para geolocalização rápida")
        print(f"  7. Cruze informações com OpenStreetMap, StreetView")

    def _dms_to_decimal(self, dms):
        """Converte DMS para coordenada decimal."""
        if not dms:
            return None
        try:
            d = dms[0][0] / dms[0][1]
            m = dms[1][0] / dms[1][1] / 60
            s = dms[2][0] / dms[2][1] / 3600
            return d + m + s
        except:
            return None

    def report(self):
        """Relatório final."""
        if self.findings:
            print(f"\n{'='*70}")
            print(f"📋 ACHADOS RESUMO:")
            print(f"{'='*70}")
            for key, value in self.findings[:10]:
                print(f"  {key}: {str(value)[:80]}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    filepath = sys.argv[1]
    verbose = '--verbose' in sys.argv
    batch = '--batch' in sys.argv

    osint = OSINTGeo(verbose=verbose)

    if batch and os.path.isdir(filepath):
        print(f"🔄 Modo batch: processando imagens em {filepath}...")
        for f in Path(filepath).glob('**/*'):
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                osint.analyze(str(f))
    else:
        osint.analyze(filepath)

    osint.report()

if __name__ == "__main__":
    main()
