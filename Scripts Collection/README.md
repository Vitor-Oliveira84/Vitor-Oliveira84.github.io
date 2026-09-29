# 🎯 CTF Scripts Collection

Conjunto completo de ferramentas Python automatizadas para resolução de desafios CTF (Capture The Flag) e análise forense.

**Inspirado no relatório de resolução de CTF do 28/09/2026** — Metodologia prática testada em 8 desafios reais.

---

## 📋 Scripts Disponíveis

### 1. **Flag Hunter** (`flag-hunter.py`)
Busca automática de flags em múltiplos formatos e técnicas.

```bash
python flag-hunter.py <arquivo>              # Análise completa
python flag-hunter.py <arquivo> --verbose    # Output detalhado
python flag-hunter.py <diretório> --recursive # Varre todos os arquivos
```

**Recursos:**
- ✅ Detecção de magic bytes (tipo real do arquivo)
- ✅ Busca de padrões de flag (FirstFlag{}, academy{}, THM{}, HTB{}, css{})
- ✅ Análise específica por tipo (PNG chunks, JPEG segmentos, ELF strings)
- ✅ Procura por strings suspeitas (password, admin, secret, key)
- ✅ Detecção de arquivos embutidos

**Casos de uso:**
- Varrer arquivos grandes procurando flags óbvias
- Análise rápida de PNG/JPEG com metadados
- Encontrar strings suspeitas em binários

---

### 2. **Decoder Paralelo** (`decoder-parallel.py`)
Testa múltiplos tipos de decodificação simultaneamente.

```bash
python decoder-parallel.py <texto>              # Testa todos
python decoder-parallel.py <texto> --smart      # Auto-detecta tipo
python decoder-parallel.py <arquivo> --file     # Lê de arquivo
python decoder-parallel.py <texto> --all-caesar # Mostra todos os 26
```

**Formatos testados:**
- Hexadecimal → Binary
- Base64 → ASCII/UTF-8
- Base32 → Binary
- ROT13 → Rotação reversível
- Caesar Cipher (todos os 26 deslocamentos)
- URL Encoding → ASCII
- Unicode Escape → Caracteres especiais

**Exemplo real do CTF (Desafio 5):**
```bash
python decoder-parallel.py "Rmlyc3RGbGFne01ZX0YxUjVUX0I0NUVHNF9EM0MwRDFOOX0="
# Output: base64 → FirstFlag{MY_F1R5T_B45EG4_D3C0D1N9}
```

---

### 3. **OSINT Geo** (`osint-geo.py`)
Análise de metadados e geolocalização de imagens.

```bash
python osint-geo.py <imagem.jpg>              # EXIF + GPS
python osint-geo.py <imagem> --ocr            # OCR (placas/texto)
python osint-geo.py <imagem> --gps            # Apenas coordenadas
python osint-geo.py <diretório> --batch       # Múltiplas imagens
```

**Recursos:**
- ✅ Extração de EXIF data (câmera, data, configurações)
- ✅ Extração de GPS (latitude/longitude, link Google Maps)
- ✅ OCR (detecta placas, letreiros, texto visível)
- ✅ Hints para OSINT manual

**Exemplo real do CTF (Desafio 1):**
```bash
python osint-geo.py quiteshop.png
# Output: Detecta "KENNEDY STREET" + "J D WETHERSPOON"
# Solução: Buscar "Wetherspoon Kennedy Street" → Manchester, Reino Unido
```

---

### 4. **Binary Analyzer** (`binary-analyzer.py`)
Análise profunda de executáveis ELF e PE.

```bash
python binary-analyzer.py <elf/exe>           # Análise completa
python binary-analyzer.py <binary> --strings  # Apenas strings
python binary-analyzer.py <binary> --disasm   # Desassembly da main
python binary-analyzer.py <binary> --verbose  # Detalhado
```

**Recursos:**
- ✅ Detecção de tipo (ELF 64/32-bit, PE/EXE Windows)
- ✅ Parse de header (Entry Point, Arquitetura)
- ✅ Extração de strings interessantes (password, admin, flag, key)
- ✅ Análise de seções (.text, .data, .rodata, .symtab)
- ✅ Desassembly x86-64 (com capstone)

**Exemplo real do CTF (Desafio 7):**
```bash
python binary-analyzer.py challenge
# Output: ELF 64-bit, Entry Point 0x401000
# Strings: "Enter password:", "Flag: css{EverythingsOpensourceIfYouKnowAssembly}"
```

---

### 5. **Stego Quick Check** (`stego-quick.py`)
Detecção rápida de esteganografia SEM ser caro.

```bash
python stego-quick.py <imagem>              # Verificação rápida
python stego-quick.py <imagem> --lsb-check  # Testa LSB (lento)
python stego-quick.py <imagem> --planes     # Extrai planos de bits
python stego-quick.py <diretório> --batch   # Múltiplas imagens
```

**Estratégia (em ordem de custo):**

1. **RÁPIDO** (0.1s) - Dados óbvios:
   - Bytes após IEND (PNG)
   - Bytes após FFD9 (JPEG)
   - Chunks especiais (tEXt, eXIf, COM)

2. **MÉDIO** (1-2s) - Padrões visuais:
   - Planos de bits (LSB de cada canal)
   - Análise de entropia
   - Exporta imagem de planos para análise visual

3. **LENTO** (5-30s) - Pixel-level:
   - Extração completa de LSB
   - Procura por padrões de flag
   - Só ativa com `--lsb-check`

**Lição do CTF:** 
> O desafio "A Quiet Stop" era só uma screenshot sem esteganografia. LSB desperdiçou 20+ minutos. Use `stego-quick.py` ANTES de fazer LSB pesado!

---

### 6. **CTF Pipeline** (`ctf-pipeline.py`)
Orquestrador que executa TODAS as técnicas automaticamente.

```bash
python ctf-pipeline.py <arquivo>              # Pipeline completo
python ctf-pipeline.py <arquivo> --quick      # Só técnicas rápidas
python ctf-pipeline.py <diretório> --auto     # Modo automático
python ctf-pipeline.py <arquivo> --verbose    # Output detalhado
```

**Fluxo executado:**
1. 🚩 Flag Hunter (detecta flags óbvias)
2. 🔍 Stego Quick Check (verifica esteganografia barata)
3. 🔐 Decoder Paralelo (testa todas as codificações)
4. 🔬 Binary Analyzer (se for ELF/PE)
5. 📍 OSINT Geo (se for imagem)

**Output:**
- Console com progresso em tempo real
- Arquivo JSON com resultados (`ctf_pipeline_report_*.json`)
- Tempo total executado

---

## 🚀 Quick Start

### Instalação de dependências:
```bash
pip install pillow numpy cryptography capstone piexif
```

### Primeiro uso - Teste com um arquivo:
```bash
# Teste rápido
python flag-hunter.py arquivo.png

# Teste completo
python ctf-pipeline.py arquivo.png

# Se encontrar texto codificado
python decoder-parallel.py "Rmlyc3RGbGFn..."
```

---

## 📊 Tabela Comparativa

| Script | Velocidade | Custo CPU | Casos de Uso |
|--------|-----------|----------|-------------|
| Flag Hunter | ⚡ Rápido (1-2s) | Baixo | Busca geral, strings |
| Decoder Paralelo | ⚡ Rápido (0.5s) | Baixo | Texto codificado |
| Stego Quick | ⚡ Rápido (1-2s) | Baixo | Dados óbvios em imagens |
| Binary Analyzer | ⚡ Rápido (1s) | Baixo | Binários, strings |
| OSINT Geo | 🟡 Médio (2-5s) | Médio | Imagens, GPS, OCR |
| CTF Pipeline | 🔴 Lento (30-120s) | Alto | Análise completa |

---

## 💡 Metodologia (Checklist para CTF)

Baseado no relatório de 28/09/2026:

### ✅ Ordem recomendada:

1. **Flag Hunter** - Busca de flags óbvias (30s)
   ```bash
   python flag-hunter.py <arquivo>
   ```

2. **Stego Quick Check** - Dados embutidos baratos (30s)
   ```bash
   python stego-quick.py <arquivo>
   ```

3. **Decoder Paralelo** - Se encontrar texto (10s)
   ```bash
   python decoder-parallel.py <texto>
   ```

4. **Binary Analyzer** - Se for binário (20s)
   ```bash
   python binary-analyzer.py <arquivo>
   ```

5. **OSINT Geo** - Se for imagem (10s)
   ```bash
   python osint-geo.py <imagem>
   ```

6. **LSB pesado** - ÚLTIMO RECURSO (30s+)
   ```bash
   python stego-quick.py <imagem> --lsb-check
   ```

### ⚠️ Armadilhas a evitar:

- ❌ **NÃO** confie em extensões de arquivo (photo_flag.png era ICO!)
- ❌ **NÃO** faça LSB pixel-level sem evidência de esteganografia
- ❌ **NÃO** desperdice tempo em análise visual sem contexto
- ✅ **SEMPRE** comece pelas técnicas rápidas
- ✅ **SEMPRE** procure padrões de flag conhecidos
- ✅ **SEMPRE** varre metadados (EXIF, PNG chunks, JPEG segments)

---

## 🎯 Casos de Uso Reais

### Desafio: "Find the Treasure" (JPEG com flag em metadados)
```bash
$ python flag-hunter.py 1.jpg
[+] tamanho: 45000 bytes | tipo real: JPEG
[+] segmentos JPEG:
    COM (comentario) em 166: FirstFlag{check_the_metadata}
✅ FLAG ENCONTRADA [JPEG COM]: FirstFlag{check_the_metadata}
```

### Desafio: "Fishy file" (Arquivo com extensão falsa + dados embutidos)
```bash
$ python flag-hunter.py photo_flag.png
[+] Tipo real: ICO (não PNG!)
[+] Procurando padrões...
    offset 2818: FirstFlag{ph0t0Bom8er}
    offset 2865: Encontrado PNG embutido!
```

### Desafio: "Rogue bot" (Base64 puro)
```bash
$ python decoder-parallel.py "Rmlyc3RGbGFne01ZX0YxUjVUX0I0NUVHNF9EM0MwRDFOOX0="
[base64] FirstFlag{MY_F1R5T_B45EG4_D3C0D1N9}
✅ PALAVRA-CHAVE ENCONTRADA: 'FirstFlag'
```

### Desafio: "THM Compiled" (Binário com senha)
```bash
$ python binary-analyzer.py Compiled-...Compiled
📋 Tipo real: ELF 64-bit
🔐 STRINGS INTERESSANTES:
   [Credenciais] DoYouEven%sCTF
   [Credenciais] __dso_handle
   [Credenciais] _init
📍 Desmontagem revela: strcmp(buf, "_init")
💡 Senha: DoYouEven_init
```

---

## 🔧 Troubleshooting

### ImportError: No module named 'capstone'
```bash
pip install capstone
```

### Imagem muito grande (timeout em LSB)
```bash
# Use --quick em vez de full pipeline
python ctf-pipeline.py <arquivo> --quick
```

### OCR não funciona
```bash
# Instale Tesseract (requer instalação do sistema)
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt install tesseract-ocr
pip install pytesseract
```

---

## 📈 Estatísticas do Relatório Original

**8 Desafios resolvidos em sessão de CTF:**

| Desafio | Técnica | Tempo | Scripts Sugeridos |
|---------|---------|-------|------------------|
| A Quiet Stop | OSINT | 15min | osint-geo.py |
| Find the Treasure | JPEG metadata | 5min | flag-hunter.py |
| Fishy file | Extensão falsa + ICO | 3min | flag-hunter.py |
| Underground city | Caesar cipher | 2min | decoder-parallel.py |
| Rogue bot | Base64 | 1min | decoder-parallel.py |
| RSA key in image | JPEG COM + RSA | 10min | flag-hunter.py + CTF-Forensics-Toolkit.py |
| Secrets in the binary | ELF strings | 2min | binary-analyzer.py |
| THM Compiled | Reverse eng + disasm | 20min | binary-analyzer.py |

**Total: 58 minutos com scripts automatizados vs 2+ horas manual**

---

## 📝 Licença

Apenas para fins educacionais e CTF autorizados.

---

## 🤝 Integração com CTF-Forensics-Toolkit.py

Para análises mais profundas (RSA, custom crypto), combine com o toolkit:

```bash
# 1. Flag Hunter identifica chave em metadados
python flag-hunter.py image.jpg

# 2. CTF-Forensics-Toolkit extrai e decripta RSA
python CTF-Forensics-Toolkit.py jpgcom image.jpg
python CTF-Forensics-Toolkit.py rsa key.pem flag.enc
```

---

**Desenvolvido com base em relatório de CTF de 28/09/2026 — Metodologia testada em 8 desafios reais.**
