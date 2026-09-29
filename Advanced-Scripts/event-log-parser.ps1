#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
Windows Event Log Parser - Detecta ataques e atividades suspeitas

.DESCRIPTION
Analisa logs do Windows: Security, System, Application
Procura por: Pass-the-Hash, Kerberoasting, Lateral Movement, Persistence, etc.

.PARAMETER LogName
Nome do log: Security, System, Application

.PARAMETER Hours
Analisar eventos das últimas N horas (default: 24)

.PARAMETER EventIDs
IDs de eventos específicos

.PARAMETER OutputFile
Salvar relatório em JSON

.EXAMPLE
.\event-log-parser.ps1 -LogName Security -Hours 48
.\event-log-parser.ps1 -LogName Security -EventIDs 4688,4720 -OutputFile report.json

.NOTES
IDs importantes:
  4720 = User account created
  4722 = User account enabled
  4723 = Password change attempt
  4688 = Process creation
  4689 = Process terminated
  4702 = Scheduled task registered
  4719 = Audit policy changed
  4720 = User created
  4722 = User enabled
  4723 = Password changed
  4756 = Member added to group
  5136 = Directory object modified
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$LogName = "Security",

    [Parameter(Mandatory=$false)]
    [int]$Hours = 24,

    [Parameter(Mandatory=$false)]
    [array]$EventIDs,

    [Parameter(Mandatory=$false)]
    [string]$OutputFile,

    [switch]$Suspicious,
    [switch]$Persistence,
    [switch]$LateralMovement,
    [switch]$CredentialDump,
    [switch]$All
)

$ErrorActionPreference = "SilentlyContinue"

# Definir padrões suspeitos
$SuspiciousPatterns = @{
    'Pass-the-Hash' = @(4624, 4768)  # Logon com hash
    'Kerberoasting' = @(4769, 4770)  # Ticket request
    'Lateral-Movement' = @(4624, 4688, 4689)  # Logon + Process
    'Persistence' = @(4697, 4698, 4702)  # Scheduled tasks
    'Credential-Dump' = @(4690, 4692)  # Credential manager
    'Privilege-Escalation' = @(4673, 4674)  # Privilege use
    'Account-Manipulation' = @(4720, 4722, 4724, 4726)  # Account events
}

function Get-LogEvents {
    param(
        [string]$LogName,
        [int]$Hours,
        [array]$EventIDs
    )

    $StartTime = (Get-Date).AddHours(-$Hours)

    $FilterHashtable = @{
        LogName   = $LogName
        StartTime = $StartTime
    }

    if ($EventIDs) {
        $FilterHashtable['ID'] = $EventIDs
    }

    Write-Host "[*] Lendo eventos do $LogName das últimas $Hours horas..." -ForegroundColor Cyan
    $events = Get-WinEvent -FilterHashtable $FilterHashtable -ErrorAction SilentlyContinue

    Write-Host "[+] $($events.Count) eventos encontrados" -ForegroundColor Green
    return $events
}

function Analyze-PassTheHash {
    param([array]$Events)

    Write-Host "`n[*] Analisando Pass-the-Hash (Logons suspeitos)..." -ForegroundColor Cyan

    $suspicious = @()
    foreach ($event in $Events) {
        if ($event.Id -eq 4624) {
            # Logon Type 3 = Network, 10 = RDP, 11 = Batch
            $xml = [xml]$event.ToXml()
            $logonType = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "LogonType"} | Select-Object -First 1 | ForEach-Object {$_.'#text'}

            if ($logonType -in @(3, 10, 11)) {
                $suspicious += @{
                    TimeCreated = $event.TimeCreated
                    Computer = $event.MachineName
                    EventID = $event.Id
                    Message = "Suspicious logon type: $logonType"
                }
            }
        }
    }

    if ($suspicious.Count -gt 0) {
        Write-Host "[!] $($suspicious.Count) eventos suspeitos detectados" -ForegroundColor Red
        $suspicious | ForEach-Object {
            Write-Host "    $($_.TimeCreated) | $($_.Computer) | $($_.Message)"
        }
    }

    return $suspicious
}

function Analyze-ScheduledTasks {
    param([array]$Events)

    Write-Host "`n[*] Analisando Scheduled Tasks (Persistence)..." -ForegroundColor Cyan

    $tasks = @()
    foreach ($event in $Events) {
        if ($event.Id -eq 4702) {
            $xml = [xml]$event.ToXml()
            $taskName = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "TaskName"} | ForEach-Object {$_.'#text'}
            $taskContent = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "TaskContentNew"} | ForEach-Object {$_.'#text'}

            if ($taskName) {
                $tasks += @{
                    TimeCreated = $event.TimeCreated
                    Computer = $event.MachineName
                    TaskName = $taskName
                }
            }
        }
    }

    if ($tasks.Count -gt 0) {
        Write-Host "[!] $($tasks.Count) scheduled tasks criadas/modificadas" -ForegroundColor Yellow
        $tasks | ForEach-Object {
            Write-Host "    $($_.TimeCreated) | $($_.TaskName)"
        }
    }

    return $tasks
}

function Analyze-ProcessCreation {
    param([array]$Events)

    Write-Host "`n[*] Analisando Process Creation..." -ForegroundColor Cyan

    $suspicious_procs = @('cmd.exe', 'powershell.exe', 'mimikatz', 'psexec', 'ncat', 'nc.exe')
    $procs = @()

    foreach ($event in $Events) {
        if ($event.Id -eq 4688) {
            $xml = [xml]$event.ToXml()
            $image = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "NewProcessName"} | ForEach-Object {$_.'#text'}
            $cmdline = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "CommandLine"} | ForEach-Object {$_.'#text'}

            if ($image) {
                foreach ($proc in $suspicious_procs) {
                    if ($image -like "*$proc*") {
                        $procs += @{
                            TimeCreated = $event.TimeCreated
                            Computer = $event.MachineName
                            Process = (Split-Path -Leaf $image)
                            CommandLine = $cmdline
                        }
                        break
                    }
                }
            }
        }
    }

    if ($procs.Count -gt 0) {
        Write-Host "[!] $($procs.Count) processos suspeitos detectados" -ForegroundColor Red
        $procs | ForEach-Object {
            Write-Host "    $($_.TimeCreated) | $($_.Process) | $($_.CommandLine)"
        }
    }

    return $procs
}

function Analyze-AccountModification {
    param([array]$Events)

    Write-Host "`n[*] Analisando Account Modifications..." -ForegroundColor Cyan

    $mods = @()
    foreach ($event in $Events) {
        if ($event.Id -in @(4720, 4722, 4724, 4726)) {
            $xml = [xml]$event.ToXml()
            $targetName = $xml.Event.EventData.Data | Where-Object {$_.Name -eq "TargetUserName"} | ForEach-Object {$_.'#text'}

            $action = @{
                4720 = "User Created"
                4722 = "User Enabled"
                4724 = "Password Reset"
                4726 = "User Deleted"
            }[$event.Id]

            if ($targetName) {
                $mods += @{
                    TimeCreated = $event.TimeCreated
                    Computer = $event.MachineName
                    Action = $action
                    TargetUser = $targetName
                }
            }
        }
    }

    if ($mods.Count -gt 0) {
        Write-Host "[*] $($mods.Count) modificações de conta detectadas" -ForegroundColor Yellow
        $mods | ForEach-Object {
            Write-Host "    $($_.TimeCreated) | $($_.Action) | $($_.TargetUser)"
        }
    }

    return $mods
}

function Generate-Report {
    param(
        [hashtable]$Results,
        [string]$OutputFile
    )

    if ($OutputFile) {
        $report = @{
            Timestamp = Get-Date
            Summary = @{
                TotalEvents = $Results.TotalEvents
                SuspiciousLogons = $Results.PassTheHash.Count
                ScheduledTasks = $Results.ScheduledTasks.Count
                SuspiciousProcesses = $Results.ProcessCreation.Count
                AccountModifications = $Results.AccountModification.Count
            }
            Details = $Results
        }

        $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Host "`n[+] Relatório salvo: $OutputFile" -ForegroundColor Green
    }
}

# === MAIN ===
Write-Host "`n$('='*70)" -ForegroundColor Cyan
Write-Host "⚠️  Windows Event Log Parser - $LogName" -ForegroundColor Red
Write-Host "$('='*70)`n" -ForegroundColor Cyan

try {
    $events = Get-LogEvents -LogName $LogName -Hours $Hours

    if ($events.Count -eq 0) {
        Write-Host "[!] Nenhum evento encontrado" -ForegroundColor Yellow
        exit
    }

    $results = @{
        TotalEvents = $events.Count
        PassTheHash = @()
        ScheduledTasks = @()
        ProcessCreation = @()
        AccountModification = @()
    }

    # Análises
    if ($Suspicious -or $All) {
        $results.PassTheHash = Analyze-PassTheHash -Events $events
    }
    if ($Persistence -or $All) {
        $results.ScheduledTasks = Analyze-ScheduledTasks -Events $events
    }
    if ($LateralMovement -or $All) {
        $results.ProcessCreation = Analyze-ProcessCreation -Events $events
    }

    $results.AccountModification = Analyze-AccountModification -Events $events

    # Relatório
    if ($OutputFile) {
        Generate-Report -Results $results -OutputFile $OutputFile
    }

    Write-Host "`n[+] Análise completa!" -ForegroundColor Green
}
catch {
    Write-Host "[!] Erro: $_" -ForegroundColor Red
}
