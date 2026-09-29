# 🔍 CrowdStrike RTR — Threat Hunting Scripts

Scripts executáveis via **Real Time Response (RTR)** do CrowdStrike para análise rápida de hosts comprometidos durante investigações de segurança.

> **Nota:** Executar como Administrator. Usar no contexto de RTR console do CrowdStrike.

---

## 📋 Índice

- [Coleta de Informações do Sistema](#coleta-de-informações-do-sistema)
- [Detecção de Persistência](#detecção-de-persistência)
- [Análise de Processos](#análise-de-processos)
- [Análise de Rede](#análise-de-rede)
- [Busca de Artefatos de Ataque](#busca-de-artefatos-de-ataque)
- [Análise de Eventos de Segurança](#análise-de-eventos-de-segurança)
- [Detecção de EDR/AV Evasion](#detecção-de-edrav-evasion)

---

## 🖥️ Coleta de Informações do Sistema

### Informações Básicas do Host
```powershell
# Sistema operacional e versão
Get-WmiObject win32_operatingsystem | Select Caption, BuildNumber, InstallDate

# Usuários locais
Get-LocalUser | Select Name, Enabled, LastLogonDate

# Grupos locais
Get-LocalGroup | Select Name

# Hotfixes/Patches instalados
Get-HotFix | Sort-Object -Property InstalledOn -Descending | Select HotFixID, Description, InstalledOn -First 10

# Variáveis de ambiente (buscar anomalias)
Get-ChildItem env: | Select Name, Value | Sort-Object Name
```

### Informações de Hardware & IP
```powershell
# Adaptadores de rede
Get-NetAdapter | Select Name, InterfaceDescription, Status

# Configuração IP
Get-NetIPAddress | Select IPAddress, InterfaceAlias, AddressFamily | Where-Object {$_.AddressFamily -eq "IPv4"}

# DNS configurado
Get-DnsClientServerAddress | Select InterfaceAlias, ServerAddresses

# MAC Address
Get-NetAdapter | Select Name, MacAddress

# Hostname e domínio
$env:COMPUTERNAME
$env:USERDOMAIN
```

---

## 🔒 Detecção de Persistência

### Run Keys (Autoexec)
```powershell
# HKLM\Software\Microsoft\Windows\CurrentVersion\Run
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object -Property * -ExcludeProperty PSPath, PSParentPath, PSChildName, PSDrive, PSProvider

# HKCU\Software\Microsoft\Windows\CurrentVersion\Run
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object -Property * -ExcludeProperty PSPath, PSParentPath, PSChildName, PSDrive, PSProvider

# RunOnce keys
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
```

### Scheduled Tasks Suspeitos
```powershell
# Listar todas as tasks
Get-ScheduledTask | Where-Object {$_.State -eq "Ready"} | Select-Object TaskName, TaskPath, Author, @{Name="Command";Expression={$_.Actions.Execute}}

# Tasks em pastas suspeitas
Get-ScheduledTask | Where-Object {$_.TaskPath -like "*Microsoft\Windows\*"} | Select TaskName, State, Author

# Buscar tasks com ações suspeitas
Get-ScheduledTask | Where-Object {$_.Actions.Execute -match "(powershell|cmd|cscript|wscript|bash|curl|wget)"} | Select TaskName, @{Name="Action";Expression={$_.Actions.Execute}}
```

### Services Suspeitos
```powershell
# Serviços que iniciam automaticamente
Get-WmiObject win32_service | Where-Object {$_.StartMode -eq "Auto"} | Select Name, DisplayName, PathName, StartMode

# Serviços em diretórios não-padrão (Red Flag)
Get-WmiObject win32_service | Where-Object {$_.PathName -notmatch "System32|SysWOW64|Program Files"} | Select Name, PathName, StartMode

# Serviços com nomes genéricos suspeitos
Get-WmiObject win32_service | Where-Object {$_.Name -match "(update|service|host|agent|monitor)"} | Select Name, DisplayName, PathName
```

### Startup Folder
```powershell
# User Startup folder
Get-ChildItem -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" -Force

# All Users Startup
Get-ChildItem -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" -Force
```

---

## ⚙️ Análise de Processos

### Processos em Execução
```powershell
# Todos os processos com caminho completo
Get-Process | Select-Object Name, ID, Path, @{Name="CommandLine";Expression={(Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)").CommandLine}} | Sort-Object Name

# Processos com CPU/Memória alta
Get-Process | Sort-Object -Property @{Expression={$_.CPU};Descending=$true} -Top 10 | Select Name, ID, CPU, @{Name="Memory(MB)";Expression={$_.WorkingSet/1MB}}

# Processos sem caminho (Red Flag)
Get-WmiObject Win32_Process | Where-Object {$_.ExecutablePath -eq $null} | Select Name, ProcessId
```

### Análise de DLL Loading
```powershell
# DLLs carregadas por um processo específico (PID 1234)
$pid = 1234  # Substituir pelo PID real
Get-Process -Id $pid | Select-Object -ExpandProperty Modules | Select-Object FileName | Sort-Object FileName

# Buscar DLLs com padrões suspeitos
Get-Process | ForEach-Object {
  $_.Modules | Where-Object {$_.FileName -match "(temp|appdata|documents|downloads)"} 
} | Select-Object FileName | Sort-Object -Unique
```

### Injeção de Processo
```powershell
# Verificar parent-child relationships anormais
Get-WmiObject Win32_Process | Select-Object ProcessId, Name, ParentProcessId, @{Name="Parent";Expression={(Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue).Name}} | Where-Object {$_.Name -ne $_.Parent}

# Processos filhos de Explorer
Get-WmiObject Win32_Process | Where-Object {$_.ParentProcessId -eq (Get-Process explorer | Select-Object -ExpandProperty Id)} | Select Name, ProcessId, CommandLine
```

---

## 🌐 Análise de Rede

### Conexões Ativas
```powershell
# Todas as conexões TCP/UDP
Get-NetTCPConnection | Where-Object {$_.State -eq "Established"} | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, @{Name="Process";Expression={(Get-Process -Id $_.OwningProcess).Name}}

# Conexões para IPs externos (não-RFC1918)
Get-NetTCPConnection | Where-Object {$_.RemoteAddress -notmatch "^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)"} | Select LocalAddress, LocalPort, RemoteAddress, RemotePort, @{Name="Process";Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name}}

# Conexões em portas não-padrão (Red Flag)
Get-NetTCPConnection | Where-Object {$_.RemotePort -notmatch "^(80|443|53|22|3389|445|3306|5432)$"} | Select RemoteAddress, RemotePort, @{Name="Process";Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).Name}}
```

### Listening Ports
```powershell
# Portas abertas para escuta
Get-NetTCPConnection | Where-Object {$_.State -eq "Listen"} | Select LocalAddress, LocalPort, @{Name="Process";Expression={(Get-Process -Id $_.OwningProcess).Name}} | Sort-Object LocalPort
```

### DNS Queries Recentes
```powershell
# DNS cache local
ipconfig /displaydns | Select-String "Record Name|Record Type|Data" | ForEach-Object {$_ -replace "\s+", " "} | Out-GridView
```

---

## 🎯 Busca de Artefatos de Ataque

### Arquivos Recentemente Modificados
```powershell
# Arquivos modificados nas últimas 24 horas
Get-ChildItem -Path $env:USERPROFILE -Recurse -File -ErrorAction SilentlyContinue | Where-Object {$_.LastWriteTime -gt (Get-Date).AddHours(-24)} | Select-Object FullName, LastWriteTime, @{Name="Size(KB)";Expression={$_.Length/1KB}} | Sort-Object LastWriteTime -Descending | Select-Object -First 50

# Executáveis recentes (últimas 48 horas)
Get-ChildItem -Path $env:USERPROFILE -Recurse -Include *.exe, *.dll, *.vbs, *.ps1 -ErrorAction SilentlyContinue | Where-Object {$_.LastWriteTime -gt (Get-Date).AddHours(-48)} | Select FullName, LastWriteTime
```

### Arquivos Temporários Suspeitos
```powershell
# Arquivos em temp folders
Get-ChildItem -Path @("$env:TEMP", "$env:WINDIR\Temp", "C:\Windows\Temp") -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName, LastAccessTime | Sort-Object LastAccessTime -Descending

# Arquivos em AppData com extensões executáveis
Get-ChildItem -Path "$env:APPDATA" -Recurse -Include *.exe, *.dll, *.vbs, *.ps1, *.bat -ErrorAction SilentlyContinue | Select FullName, LastWriteTime
```

### Downloads Suspeitos
```powershell
# Arquivos em Downloads
Get-ChildItem -Path "$env:USERPROFILE\Downloads" -File -ErrorAction SilentlyContinue | Select-Object FullName, CreationTime, LastWriteTime | Sort-Object LastWriteTime -Descending

# Arquivos com Zone.Identifier (Downloaded from Internet)
Get-Item -Path "$env:USERPROFILE\Downloads\*" -Stream Zone.Identifier -ErrorAction SilentlyContinue | Select-Object FileName
```

---

## 📊 Análise de Eventos de Segurança

### Logons Recentes
```powershell
# Últimos 50 logons bem-sucedidos
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4624} -MaxEvents 50 | Select-Object TimeCreated, @{Name="User";Expression={$_.Properties[5].Value}}, @{Name="Source";Expression={$_.Properties[18].Value}}, @{Name="LogonType";Expression={$_.Properties[8].Value}} | Sort-Object TimeCreated -Descending
```

### Account Lockouts
```powershell
# Lockouts (ID 4740)
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4740} -MaxEvents 20 | Select-Object TimeCreated, @{Name="Account";Expression={$_.Properties[0].Value}} | Sort-Object TimeCreated -Descending
```

### Failed Logons
```powershell
# Failed logons (ID 4625)
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625} -MaxEvents 50 | Select-Object TimeCreated, @{Name="Account";Expression={$_.Properties[5].Value}}, @{Name="Source";Expression={$_.Properties[18].Value}} | Sort-Object TimeCreated -Descending | Select-Object -First 20
```

### Privilege Escalation Attempts
```powershell
# Token Elevation (ID 4672)
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4672} -MaxEvents 30 | Select-Object TimeCreated, @{Name="User";Expression={$_.Properties[1].Value}}, @{Name="Process";Expression={$_.Properties[5].Value}} | Sort-Object TimeCreated -Descending
```

---

## 🛡️ Detecção de EDR/AV Evasion

### Verificar Defesas Ativas
```powershell
# Windows Defender status
Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, IoPScanningSupported, BehaviorMonitoringEnabled, OnAccessProtectionEnabled

# Firewall status
Get-NetFirewallProfile | Select-Object Name, Enabled

# Antivírus registrado
Get-WmiObject -Namespace "root\SecurityCenter2" -Class AntiVirusProduct | Select-Object DisplayName, ProductState
```

### Detecção de Instrumentação Disabled
```powershell
# ETW (Event Tracing for Windows) traces
wevtutil.exe el | Select-String -Pattern "Operational|Analytic"

# WMI Event Subscriptions (Usado em evasão)
Get-WmiObject -Namespace root\subscription -Class __EventFilter | Select-Object Name, Query

Get-WmiObject -Namespace root\subscription -Class __EventConsumer | Select-Object Name
```

### PowerShell Execution Policy & Logging
```powershell
# Execution Policy
Get-ExecutionPolicy -List

# PowerShell logging habilitado?
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
```

---

## 📝 Exemplo de Fluxo de Hunting

```powershell
# 1. Verificar processos suspeitos
Get-Process | Where-Object {$_.ProcessName -match "(svchost|explorer|notepad)"} | Select Name, ID

# 2. Extrair CommandLine
$proc = Get-Process -Id 1234  # PID suspeito
Get-WmiObject Win32_Process -Filter "ProcessId=$($proc.Id)" | Select CommandLine

# 3. Verificar conexões
Get-NetTCPConnection | Where-Object {$_.OwningProcess -eq $proc.Id} | Select RemoteAddress, RemotePort

# 4. Listar DLLs carregadas
$proc | Select-Object -ExpandProperty Modules | Select FileName

# 5. Buscar persistência
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object $proc.Name

# 6. Coletar para análise
Write-Output "Processo: $($proc.Name), PID: $($proc.Id)"
```

---

## ⚠️ IOCs Comuns para Buscar

```powershell
# Padrões de detecção
$suspiciousPatterns = @(
    "powershell.*-enc",
    "cmd.*\/c.*http",
    "certutil.*http",
    "bitsadmin.*transfer",
    "psexec",
    "mimikatz",
    "pass.*hash",
    "golden.*ticket",
    "admin\$"
)

# Buscar em event logs
foreach ($pattern in $suspiciousPatterns) {
    Get-WinEvent -FilterHashtable @{LogName='System'} -MaxEvents 1000 | 
    Where-Object {$_.Message -match $pattern} | 
    Select-Object TimeCreated, @{Name="Pattern";Expression={$pattern}}
}
```

---

## 🔧 Quick Reference — Comandos Mais Usados

| Objetivo | Comando |
|----------|---------|
| **Processos suspeitos** | `Get-Process \| Sort-Object CPU -Desc \| Select -First 10` |
| **Conexões de rede** | `Get-NetTCPConnection \| Where {$_.State -eq "Established"}` |
| **Persistência via Registry** | `Get-ItemProperty "HKLM:\Software\...\Run"` |
| **Tasks agendadas** | `Get-ScheduledTask \| Where {$_.State -eq "Ready"}` |
| **Eventos de segurança** | `Get-WinEvent -FilterHashtable @{LogName='Security'} -MaxEvents 100` |
| **Arquivos recentes** | `Get-ChildItem -Recurse \| Sort LastWriteTime -Desc` |
| **Usuários & Logons** | `Get-LocalUser \| Sort LastLogonDate -Desc` |

---

## 🔎 Script Adaptável — Busca de Arquivos/Pastas Suspeitos

### Uso Genérico para Qualquer Padrão de Busca

```powershell
# ==========================================
# THREAT HUNTING - Busca Genérica Adaptável
# ==========================================
# 
# Uso: .\Hunt-SuspiciousFiles.ps1 -Pattern "*.exe" -IncludeContent
#      .\Hunt-SuspiciousFiles.ps1 -Filename "malware" -ExcludeSystem32
#      .\Hunt-SuspiciousFiles.ps1 -Extension "js" -CalculateHash

param(
    [string]$Pattern = "*",           # Padrão de arquivo (ex: "*.js", "malware*")
    [string]$Filename,                # Nome específico do arquivo (ex: "jfbfb.js")
    [string]$Extension,               # Extensão específica (ex: "exe", "dll", "vbs")
    [string[]]$SearchPaths = @(
        "C:\Users",
        "C:\Windows\Temp",
        "C:\ProgramData",
        "$env:APPDATA",
        "$env:LOCALAPPDATA",
        "$env:USERPROFILE\Downloads"
    ),
    [switch]$CalculateHash,           # Calcular SHA256
    [switch]$IncludeContent,          # Mostrar primeiras linhas do arquivo
    [switch]$ExcludeSystem32,         # Excluir System32
    [int]$ContentLines = 5,           # Quantas linhas do conteúdo mostrar
    [long]$MinSize,                   # Tamanho mínimo em bytes
    [long]$MaxSize                    # Tamanho máximo em bytes
)

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CrowdStrike RTR - Threat Hunting Adaptável              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nParâmetros de busca:" -ForegroundColor Yellow
Write-Host "  Padrão: $Pattern"
if ($Filename) { Write-Host "  Filename: $Filename" }
if ($Extension) { Write-Host "  Extensão: *.$Extension" }
Write-Host "  Caminhos: $($SearchPaths.Count) diretórios"
Write-Host "  Calcular Hash: $CalculateHash"
Write-Host "  Mostrar conteúdo: $IncludeContent"
Write-Host ""

# Construir filtro dinâmico
if ($Extension) {
    $searchFilter = "*.$Extension"
} elseif ($Filename) {
    $searchFilter = $Filename
} else {
    $searchFilter = $Pattern
}

$foundCount = 0
$resultsArray = @()

# Buscar em cada caminho
foreach ($path in $SearchPaths) {
    if (Test-Path $path) {
        Write-Host "🔍 Procurando em: $path" -ForegroundColor Cyan
        
        try {
            $files = Get-ChildItem -Path $path -Filter $searchFilter -Recurse -ErrorAction SilentlyContinue -Force
            
            foreach ($file in $files) {
                # Filtrar por tamanho se especificado
                if ($MinSize -and $file.Length -lt $MinSize) { continue }
                if ($MaxSize -and $file.Length -gt $MaxSize) { continue }
                
                # Excluir System32 se solicitado
                if ($ExcludeSystem32 -and $file.FullName -match "System32|SysWOW64") { continue }
                
                $foundCount++
                Write-Host ""
                Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
                Write-Host "✓ ENCONTRADO: $($file.FullName)" -ForegroundColor Red
                Write-Host "  📊 Tamanho: $($file.Length) bytes ($([math]::Round($file.Length/1MB, 2)) MB)"
                Write-Host "  📅 Modificado: $($file.LastWriteTime)"
                Write-Host "  👤 Owner: $(try {(Get-Acl $file.FullName).Owner} catch {'N/A'})"
                
                # Atributos
                Write-Host "  🏷️  Atributos: $($file.Attributes)"
                
                # Calcular SHA256
                if ($CalculateHash) {
                    $hash = Get-FileHash -Path $file.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue
                    if ($hash) {
                        Write-Host "  🔐 SHA256: $($hash.Hash)" -ForegroundColor Green
                        $resultsArray += @{
                            FullName = $file.FullName
                            Size = $file.Length
                            Modified = $file.LastWriteTime
                            SHA256 = $hash.Hash
                        }
                    }
                }
                
                # Mostrar conteúdo (primeiras linhas)
                if ($IncludeContent -and ($file.Extension -match "\.txt|\.js|\.vbs|\.ps1|\.bat|\.cmd")) {
                    Write-Host "  📄 Conteúdo (primeiras $ContentLines linhas):"
                    try {
                        $content = Get-Content -Path $file.FullName -TotalCount $ContentLines -ErrorAction SilentlyContinue
                        if ($content) {
                            $content | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
                        }
                    } catch {
                        Write-Host "     [Não foi possível ler o conteúdo]" -ForegroundColor Gray
                    }
                }
                
                Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ⚠️  Erro ao pesquisar: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠️  Caminho não encontrado: $path" -ForegroundColor Yellow
    }
}

# Resumo final
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                        RESUMO                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "Total encontrado: $foundCount arquivo(s)" -ForegroundColor $(if ($foundCount -gt 0) {"Red"} else {"Green"})

if ($CalculateHash -and $resultsArray.Count -gt 0) {
    Write-Host "`nHashes SHA256 para correlação:" -ForegroundColor Yellow
    $resultsArray | ForEach-Object {
        Write-Host "$($_.SHA256) - $($_.FullName)" -ForegroundColor Green
    }
}

Write-Host ""
```

### Exemplos de Uso

```powershell
# 1. Procurar por um arquivo específico
.\Hunt-SuspiciousFiles.ps1 -Filename "jfbfb.js" -CalculateHash

# 2. Procurar por extensão suspeita
.\Hunt-SuspiciousFiles.ps1 -Extension "vbs" -IncludeContent -ContentLines 10

# 3. Procurar por executáveis em Downloads
.\Hunt-SuspiciousFiles.ps1 -Extension "exe" -SearchPaths "$env:USERPROFILE\Downloads" -CalculateHash

# 4. Procurar com padrão genérico (malware*)
.\Hunt-SuspiciousFiles.ps1 -Pattern "malware*" -CalculateHash -IncludeContent

# 5. Buscar arquivos PowerShell suspeitos (excluindo System32)
.\Hunt-SuspiciousFiles.ps1 -Extension "ps1" -ExcludeSystem32 -CalculateHash

# 6. Procurar por arquivos entre 1MB e 5MB
.\Hunt-SuspiciousFiles.ps1 -Extension "exe" -MinSize 1048576 -MaxSize 5242880 -CalculateHash

# 7. Procurar em caminho customizado
.\Hunt-SuspiciousFiles.ps1 -Pattern "*.dll" -SearchPaths "C:\Program Files", "C:\Program Files (x86)" -CalculateHash

# 8. Busca combinada (extensão + tamanho + hash)
.\Hunt-SuspiciousFiles.ps1 -Extension "zip" -MinSize 1000000 -CalculateHash -IncludeContent
```

### Variáveis Úteis para Customização

```powershell
# Padrões comuns de IOCs
$iocsToHunt = @{
    "Ransomware" = @("*.exe", "*encrypt*", "*crypt*", "*payment*")
    "Webshell" = @("*.php", "*.jsp", "*.aspx", "shell*")
    "Scripts" = @("*.vbs", "*.js", "*.ps1", "*.bat")
    "Archives" = @("*.zip", "*.rar", "*.7z", "*.iso")
    "Backdoor" = @("*backdoor*", "*shell*", "*remote*")
}

# Pastas típicas de infecção
$infectionPaths = @(
    "$env:USERPROFILE\Downloads",
    "$env:APPDATA\Local\Temp",
    "C:\Windows\Temp",
    "C:\Users\Public",
    "$env:USERPROFILE\AppData\Roaming"
)

# Procurar por cada IOC
foreach ($category in $iocsToHunt.Keys) {
    Write-Host "`nBuscando $category..." -ForegroundColor Cyan
    foreach ($pattern in $iocsToHunt[$category]) {
        Write-Host "  Padrão: $pattern"
        # Executar .\Hunt-SuspiciousFiles.ps1 -Pattern $pattern ...
    }
}
```

---

## ⚖️ Disclaimer

Apenas use em **ambientes autorizados** com **ROE assinado**. Hunting em sistemas não autorizados é ilegal.

**Use responsavelmente em:**
- ✅ Investigação de incidentes autorizados
- ✅ Testes de penetração com permissão
- ✅ Análise defensiva em ambiente corporativo
- ✅ CTF e ambientes de labs

---
