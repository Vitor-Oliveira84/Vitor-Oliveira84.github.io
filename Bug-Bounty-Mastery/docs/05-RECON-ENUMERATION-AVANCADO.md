# 🔍 RECON & ENUMERATION AVANÇADO - Bug Bounty

Descobrir TUDO sobre o alvo antes de testar vulnerabilidades

---

## 1️⃣ SUBDOMAIN ENUMERATION

### Ferramentas

```bash
# Subfinder
subfinder -d target.com -o subdomains.txt

# Assetfinder
assetfinder --subs-only target.com

# Amass
amass enum -d target.com

# Combine all
cat subdomains.txt | sort -u > all_subs.txt

# Resultado típico: 100-500 subdomínios
```

### Validar Subdomínios

```bash
# Alive check com httpx
cat all_subs.txt | httpx -silent -title -status-code > alive_subs.txt

# Resultado: ~20-50 subdomínios vivos
```

---

## 2️⃣ PORT SCANNING AVANÇADO

### Com Nmap

```bash
# Scan rápido
nmap -p- --open -sV target.com

# Resultado esperado:
# 22/tcp   SSH
# 80/tcp   HTTP
# 443/tcp  HTTPS
# 8080/tcp HTTP-PROXY
```

---

## 3️⃣ TECHNOLOGY FINGERPRINTING

### Ferramentas

```bash
# Wappalyzer
# Detecta: WordPress, React, Node.js, etc

# Nuclei
nuclei -u https://target.com -t ~/nuclei-templates/

# Resultado:
# - Framework: Flask 1.1.2 (desatualizado!)
# - CMS: WordPress 5.0 (vulnerável)
# - Server: Apache 2.4.29
```

---

## 4️⃣ HIDDEN FILES/DIRECTORIES

### Com FFUF

```bash
# Descobrir directories
ffuf -w wordlist.txt -u https://target.com/FUZZ -o results.txt

# Resultados comuns:
# /admin
# /api
# /api/v1
# /api/v2
# /backup
# /config
# /.env
# /.git
```

### Com Burp Suite

```
1. Proxy → Options → Add Match and Replace
2. Add payload para cada diretório
3. Ferramenta Burp → Content Discovery
```

---

## 5️⃣ API ENDPOINT DISCOVERY

### JavaScript Analysis

```bash
# Extrair URLs do JS
cat target.js | grep -oE 'https?://[^\s"]+' | sort -u

# Procurar por /api/
grep -r "/api/" *.js

# Resultado:
# /api/users
# /api/products
# /api/orders
# /api/admin
```

### Burp Suite Method

```
1. Proxy → HTTP History
2. Filter: /api/
3. Analise todos endpoints
4. Documente métodos (GET, POST, PUT, DELETE)
```

---

## 6️⃣ GITHUB RECON

### Procurar por Secrets

```bash
# Procurar por credentials
git log -p --all | grep -i "password\|secret\|api_key\|token"

# Procurar em commits públicos
git log --oneline | head -20

# Resultado comum: API keys, senhas, tokens expostos!
```

### GitRob/Truffles

```bash
# Procurar padrões de secrets
trufflehog filesystem . --json

# Detecta:
# - AWS_ACCESS_KEY
# - PRIVATE_KEY
# - DATABASE_PASSWORD
```

---

## 7️⃣ BURP SUITE AUTOMATION

### Scope Configuration

```
1. Target → Scope
2. Add target.com
3. Include All Subdomains
4. Include paths matching: /api/*
```

### Crawler Configuration

```
1. Scanner → Options → Crawl Settings
2. Enable JavaScript parsing
3. Maximum crawl depth: 5
4. Deixar rodar por 2-4 horas
```

---

## 📊 RECON TEMPLATE

```
TARGET: example.com

SUBDOMÍNIOS VIVOS (25):
- api.example.com
- admin.example.com
- dev.example.com
- staging.example.com
...

TECNOLOGIAS:
- Framework: Django 3.1.2
- Server: Nginx 1.18
- CMS: WordPress 5.8
- Languages: Python, JavaScript, PHP

ENDPOINTS DESCOBERTOS (50+):
GET /api/users
POST /api/users
GET /api/products
POST /api/products
DELETE /api/admin
...

DIRETÓRIOS SENSÍVEIS:
/admin
/backup
/config
/test
...

SECRETS ENCONTRADOS:
- 3 API keys no GitHub
- 2 senhas em comentários
- 1 database password

PRÓXIMAS AÇÕES:
[ ] Testar endpoints API
[ ] Procurar por SQLi
[ ] Procurar por BOLA/IDOR
[ ] Testar autenticação
```

---

**Próximo:** Volte para [BUG-BOUNTY-MASTER-README.md](./BUG-BOUNTY-MASTER-README.md)

