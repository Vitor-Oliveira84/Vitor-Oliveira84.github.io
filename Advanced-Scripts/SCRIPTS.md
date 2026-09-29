# ⚡ Quick Reference - Advanced Scripts

## 🔥 Top 5 (Implementar HOJE)

| # | Script | Comando | ROI |
|-|--------|---------|-----|
| 1 | **ad-enum-exploit.py** | `python ad-enum-exploit.py --domain lab.local --full-enum` | ⭐⭐⭐ |
| 2 | **subdomain-enum.py** | `python subdomain-enum.py -d example.com --fuzzing` | ⭐⭐⭐ |
| 3 | **event-log-parser.ps1** | `.\event-log-parser.ps1 -LogName Security -All` | ⭐⭐⭐ |
| 4 | **port-scan-parallel.sh** | `./port-scan-parallel.sh -t 192.168.0.0/24` | ⭐⭐⭐ |
| 5 | **sqli-waf-bypass.py** | `python sqli-waf-bypass.py -u "http://..." -p id` | ⭐⭐ |

---

## 📊 Todos os 12 Scripts

### **Python Scripts** (8)

```bash
# 1. Active Directory
python ad-enum-exploit.py --domain lab.local --full-enum

# 2. Subdomains  
python subdomain-enum.py -d example.com --fuzzing

# 3. S3 Buckets
python s3-bucket-enum.py -d example.com --fuzzing

# 4. SQLi WAF
python sqli-waf-bypass.py -u "http://example.com/search?q=" -p id

# 5. OSINT APIs
python osint-api-wrapper.py --full-recon example.com

# 6. Credential Stuffing
python credential-stuffing.py -c user:pass -s github,aws,azure

# 7. Google Dorks
python google-dorks.py -d example.com --all

# 8. XXE/SSRF
python xxe-ssrf-payloader.py -u "http://example.com" -t both

# 9. LDAP Injection
python ldap-injection.py -u "http://example.com/search"
```

### **PowerShell Scripts** (2)

```powershell
# 1. Event Log Parser
.\event-log-parser.ps1 -LogName Security -All

# 2. Registry Dump
.\registry-dump.ps1 -FullDump
```

### **Bash Scripts** (2)

```bash
# 1. Port Scan
./port-scan-parallel.sh -t 192.168.0.0/24

# 2. SSL Analyzer
./ssl-cert-analyzer.sh -d example.com --ct-logs
```

---

## 🎯 Por Objetivo

### **Reconhecimento**
```bash
python subdomain-enum.py -d target.com --fuzzing
python osint-api-wrapper.py --full-recon target.com
./ssl-cert-analyzer.sh -d target.com --ct-logs
python google-dorks.py -d target.com --all
./port-scan-parallel.sh -t discovered_ips
```

### **Web Testing**
```bash
python sqli-waf-bypass.py -u "http://app" -p param
python xxe-ssrf-payloader.py -u "http://app" -t both
python ldap-injection.py -u "http://app" -p username
```

### **Active Directory**
```bash
python ad-enum-exploit.py --domain corp.local --full-enum
python ad-enum-exploit.py --domain corp.local --kerberoasting
```

### **AWS Security**
```bash
python s3-bucket-enum.py -d company.com --fuzzing
python credential-stuffing.py -c user:pass -s aws
```

### **Threat Hunting**
```powershell
.\event-log-parser.ps1 -LogName Security -All
.\registry-dump.ps1 -FullDump
```

---

## ⏱️ Tempo de Execução

| Script | Tempo |
|--------|-------|
| ad-enum-exploit.py | 1-5 min |
| subdomain-enum.py | 5-15 min |
| event-log-parser.ps1 | 2-5 min |
| port-scan-parallel.sh | 2-30 min |
| sqli-waf-bypass.py | 1-5 min |
| s3-bucket-enum.py | 2-10 min |
| osint-api-wrapper.py | 5-10 min |
| credential-stuffing.py | 5-30 min |
| google-dorks.py | 10-20 min |
| ssl-cert-analyzer.sh | 1-2 min |
| ldap-injection.py | 2-5 min |
| xxe-ssrf-payloader.py | 3-8 min |
| registry-dump.ps1 | <1 min |

---

## 🆘 Troubleshooting

| Erro | Solução |
|------|---------|
| Module not found | `pip install -r requirements.txt` |
| Permission denied | `sudo` ou Run As Admin |
| Connection timeout | Aumentar timeout, verificar firewall |
| Rate limited | Adicionar delay |
| API key inválida | Verificar variáveis de ambiente |

---

**ROI: 500-800% em eficiência**
