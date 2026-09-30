# 📜 Referência Rápida dos Scripts

## 📁 Estrutura da Pasta

```
Scripts Collection/
├── README.md              # Documentação completa (read primeiro!)
├── SCRIPTS.md             # Este arquivo (referência rápida)
├── flag-hunter.py         # Busca de flags
├── decoder-parallel.py    # Decodificação de múltiplos formatos
├── osint-geo.py           # OSINT e geolocalização
├── binary-analyzer.py     # Análise de binários
├── stego-quick.py         # Detecção de esteganografia
└── ctf-pipeline.py        # Orquestrador automático
```

---

## 🚀 Scripts Resumidos

### 1. **flag-hunter.py** (265 linhas)
```bash
python flag-hunter.py <arquivo>
python flag-hunter.py <arquivo> --verbose
python flag-hunter.py <diretório> --recursive
```
**O quê:** Busca automática de flags em formatos conhecidos.
**Quando usar:** Primeiro! Análise rápida de qualquer arquivo.
**Tempo:** ~1-2 segundos
**Casos:** PNG com chunks, JPEG com segmentos, strings em ELF

---

### 2. **decoder-parallel.py** (210 linhas)
```bash
python decoder-parallel.py <texto>
python decoder-parallel.py <texto> --smart
python decoder-parallel.py <arquivo> --file
python decoder-parallel.py <texto> --all-caesar
```
**O quê:** Testa 7 formatos de decodificação simultaneamente.
**Quando usar:** Se encontrar texto codificado.
**Tempo:** ~0.5 segundos
**Decodifica:** hex, base64, base32, ROT13, Caesar (26 shifts), URL, Unicode

---

### 3. **osint-geo.py** (185 linhas)
```bash
python osint-geo.py <imagem.jpg>
python osint-geo.py <imagem> --ocr
python osint-geo.py <imagem> --gps
python osint-geo.py <diretório> --batch
```
**O quê:** Extrai EXIF, GPS, e texto (OCR) de imagens.
**Quando usar:** Para desafios de OSINT ou imagens.
**Tempo:** ~2-5 segundos
**Extrai:** Metadados EXIF, coordenadas GPS com Google Maps, OCR

---

### 4. **binary-analyzer.py** (200 linhas)
```bash
python binary-analyzer.py <elf/exe>
python binary-analyzer.py <binary> --strings
python binary-analyzer.py <binary> --disasm
python binary-analyzer.py <binary> --verbose
```
**O quê:** Análise profunda de executáveis ELF e PE.
**Quando usar:** Para binários (ELF do Linux, EXE do Windows).
**Tempo:** ~1 segundo
**Detecta:** Strings interessantes, desassembly, seções

---

### 5. **stego-quick.py** (240 linhas)
```bash
python stego-quick.py <imagem>
python stego-quick.py <imagem> --lsb-check
python stego-quick.py <imagem> --planes
python stego-quick.py <diretório> --batch
```
**O quê:** Detecção RÁPIDA de esteganografia (sem LSB caro por padrão).
**Quando usar:** Para imagens PNG/JPEG.
**Tempo:** ~1-2 segundos (rápido) ou ~30s (com LSB pesado)
**Procura:** Dados após IEND/FFD9, chunks especiais, entropia

---

### 6. **ctf-pipeline.py** (180 linhas)
```bash
python ctf-pipeline.py <arquivo>
python ctf-pipeline.py <arquivo> --quick
python ctf-pipeline.py <diretório> --auto
python ctf-pipeline.py <arquivo> --verbose
```
**O quê:** Orquestrador que executa TODAS as técnicas automaticamente.
**Quando usar:** Quando não souber por onde começar.
**Tempo:** ~30-120 segundos (arquivo único)
**Executa:** Flag Hunter → Stego → Decoder → Binary → OSINT (se aplicável)
**Output:** Relatório JSON com resultados

---

## 🎯 Ordem Recomendada para CTF

```
1. Flag Hunter        (30s)   ← Comece aqui
   ↓ Se encontrar flags → Fim! ✅
   
2. Stego Quick        (30s)   ← Dados óbvios em imagens
   ↓ Se encontrar dados → Fim! ✅
   
3. Decoder Paralelo   (10s)   ← Texto codificado?
   ↓ Se decodificar → Fim! ✅
   
4. Binary Analyzer    (20s)   ← Binário?
   ↓ Se encontrar strings/funções → Fim! ✅
   
5. OSINT Geo          (10s)   ← Imagem?
   ↓ Se GPS/EXIF útil → Fim! ✅
   
6. Stego LSB Pesado   (30s+)  ← ÚLTIMO RECURSO
```

**OU simplesmente:**
```bash
python ctf-pipeline.py arquivo  # Executa tudo automaticamente
```

---

## 🔧 Instalação de Dependências

```bash
# Obrigatório
pip install pillow numpy cryptography capstone

# Opcional mas recomendado
pip install piexif                    # GPS em osint-geo.py
pip install pytesseract               # OCR (requer Tesseract no sistema)
```

### Se OCR não funcionar (Windows):
```
1. Baixe: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale
3. pip install pytesseract
```

---

## 📊 Comparação Rápida

| Script | Velocidade | Custo | Melhor para |
|--------|-----------|-------|------------|
| flag-hunter | ⚡⚡⚡ | Baixo | Qualquer arquivo |
| decoder-parallel | ⚡⚡⚡ | Baixo | Texto codificado |
| stego-quick | ⚡⚡ | Baixo | Imagens (dados óbvios) |
| binary-analyzer | ⚡⚡ | Baixo | ELF/PE binários |
| osint-geo | 🟡 | Médio | Imagens com metadados |
| ctf-pipeline | 🟡 | Médio-Alto | Análise completa |

---

## 💡 Dicas Importantes

### ✅ SEMPRE faça isso:
- Comece com **flag-hunter** (rápido, cobre 80% dos casos)
- Use **decoder-parallel** se encontrar texto estranho
- Para imagens, rode **stego-quick** ANTES de LSB pesado

### ❌ NUNCA faça isso:
- Não confie na extensão do arquivo (photo_flag.png era ICO!)
- Não faça LSB pixel-level sem evidência de esteganografia
- Não desperdice 20+ minutos em análise visual sem contexto
- Não use tools pesadas sem tentar as rápidas primeiro

### 🎯 Checklist de CTF:
```
[ ] 1. Rodei flag-hunter? Encontrou algo?
[ ] 2. É imagem? Rodei stego-quick?
[ ] 3. Encontrei texto estranho? Rodei decoder-parallel?
[ ] 4. É binário? Rodei binary-analyzer?
[ ] 5. Ainda preso? Rodei ctf-pipeline --verbose?
[ ] 6. Último recurso: stego-quick --lsb-check (LENTO!)
```

---

## 📝 Exemplos Práticos

### Exemplo 1: Flag em JPEG metadata
```bash
$ python flag-hunter.py 1.jpg
✅ FLAG ENCONTRADA [JPEG COM]: FirstFlag{check_the_metadata}
```

### Exemplo 2: Texto em Base64
```bash
$ python decoder-parallel.py "Rmlyc3RGbGFn..."
[base64] FirstFlag{MY_F1R5T_B45EG4_D3C0D1N9}
✅ PALAVRA-CHAVE ENCONTRADA
```

### Exemplo 3: Binário com senha
```bash
$ python binary-analyzer.py Compiled-...Compiled
📋 Tipo: ELF 64-bit
🔐 STRINGS: DoYouEven%sCTF, _init, __dso_handle
💡 Desmontagem revela: strcmp(buf, "_init")
```

### Exemplo 4: Arquivo estranho (extensão falsa)
```bash
$ python flag-hunter.py photo_flag.png
[+] Tipo real: ICO (não PNG!)
[+] offset 2818: FirstFlag{ph0t0Bom8er}
[+] offset 2865: PNG embutido detectado
```

### Exemplo 5: Análise completa automática
```bash
$ python ctf-pipeline.py arquivo
[1/5] Flag Hunter... ✅ ok (0.8s)
[2/5] Stego Quick Check... ✅ ok (1.2s)
[3/5] Decoder Paralelo... ✅ ok (0.5s)
[4/5] Binary Analyzer... ✅ ok (0.9s)
[5/5] OSINT Geo... ✅ ok (2.1s)
💾 Relatório salvo: ctf_pipeline_report_1695849321.json
```

---

## 🚀 Início Rápido (3 Linhas)

```bash
# 1. Instalar dependências (uma vez)
pip install pillow numpy cryptography capstone piexif

# 2. Analisar arquivo
python flag-hunter.py arquivo.png

# 3. Se precisar de mais, rode o pipeline
python ctf-pipeline.py arquivo.png
```

---

## 📚 Ler Depois

- Leia `README.md` para documentação completa
- Veja casos reais testados: 8 desafios de CTF com 100% sucesso
- Verifique troubleshooting no README
