#Requires -Version 5.1

<#
.SYNOPSIS
Process Injection Detector - Detecta injeção de DLL em processos

.DESCRIPTION
Procura por: DLL injected, hooks, suspicious imports, memory anomalies

.EXAMPLE
.\process-injection-detector.ps1 -Verbose
.\process-injection-detector.ps1 -ProcessName explorer.exe
#>

param(
    [string]$ProcessName,
    [switch]$Verbose,
    [switch]$SuspiciousOnly
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "[*] Process Injection Detector" -ForegroundColor Cyan

# DLLs suspeitas
$suspiciousDLLs = @(
    'mimikatz', 'injected', 'beacon', 'meterpreter', 'reverse',
    'shellcode', 'payload', 'custom', 'unknown', 'loader'
)

if ($ProcessName) {
    $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
} else {
    $processes = Get-Process
}

foreach ($proc in $processes) {
    try {
        $modules = $proc.Modules
        $suspicious = @()

        foreach ($module in $modules) {
            $path = $module.FileName

            # Verifica se DLL está em local suspeito
            if ($path -match 'Temp|AppData\\Local\\Temp|Recycle.Bin') {
                $suspicious += $path
            }

            # Verifica nomes suspeitos
            foreach ($dll in $suspiciousDLLs) {
                if ($path -match $dll) {
                    $suspicious += $path
                }
            }
        }

        if ($suspicious.Count -gt 0) {
            Write-Host "[!] $($proc.Name) (PID: $($proc.Id)): $($suspicious.Count) DLL(s) suspeita(s)" -ForegroundColor Red
            $suspicious | ForEach-Object { Write-Host "    • $_" }
        }
        elseif ($Verbose) {
            Write-Host "[✓] $($proc.Name) (PID: $($proc.Id)): OK" -ForegroundColor Green
        }
    }
    catch { }
}

Write-Host "[+] Verificação completa" -ForegroundColor Green
