#Requires -Version 5.1

<#
.SYNOPSIS
Persistence Checker - Detecta backdoors e persistence mechanisms

.EXAMPLE
.\persistence-checker.ps1 -All
.\persistence-checker.ps1 -ScheduledTasks -Services
#>

param(
    [switch]$RunKeys,
    [switch]$ScheduledTasks,
    [switch]$Services,
    [switch]$StartupFolders,
    [switch]$All
)

Write-Host "[*] Persistence Checker" -ForegroundColor Cyan

# Run Keys
if ($RunKeys -or $All) {
    Write-Host "`n[*] Verificando Run Keys..." -ForegroundColor Yellow
    $paths = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
    )

    foreach ($path in $paths) {
        Get-ItemProperty -Path $path | ForEach-Object {
            $_.PSObject.Properties | Where-Object {$_.Name -notmatch "PS"} | ForEach-Object {
                Write-Host "  [!] $($_.Name): $($_.Value)"
            }
        }
    }
}

# Scheduled Tasks
if ($ScheduledTasks -or $All) {
    Write-Host "`n[*] Verificando Scheduled Tasks..." -ForegroundColor Yellow
    Get-ScheduledTask | Where-Object {$_.Author -notmatch "Microsoft"} | ForEach-Object {
        Write-Host "  [!] $($_.TaskName) - $($_.Author)"
    }
}

# Services
if ($Services -or $All) {
    Write-Host "`n[*] Verificando Services..." -ForegroundColor Yellow
    Get-Service | Where-Object {$_.StartType -eq "Automatic"} | ForEach-Object {
        $svc = Get-ItemProperty "HKLM:\System\CurrentControlSet\Services\$($_.Name)" -ErrorAction SilentlyContinue
        if ($svc.ImagePath -match "Temp|AppData") {
            Write-Host "  [!] $($_.Name): $($svc.ImagePath)"
        }
    }
}

# Startup Folders
if ($StartupFolders -or $All) {
    Write-Host "`n[*] Verificando Startup Folders..." -ForegroundColor Yellow
    $folders = @(
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
    )

    foreach ($folder in $folders) {
        if (Test-Path $folder) {
            Get-ChildItem $folder | ForEach-Object {
                Write-Host "  [!] $_"
            }
        }
    }
}

Write-Host "`n[+] Verificação completa" -ForegroundColor Green
