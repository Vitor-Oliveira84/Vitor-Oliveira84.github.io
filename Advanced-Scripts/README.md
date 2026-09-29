# 🔥 Advanced Scripts Collection

Conjunto profissional de scripts para **Red Team**, **Pentest**, e **Threat Hunting** em operações reais.

**11 Scripts essenciais testados em engagements de segurança**

---

## 📋 Scripts Inclusos (20 Total)

### **PYTHON SCRIPTS (9)**

### **1. ad-enum-exploit.py** (Python)
**Active Directory Enumeration & Exploitation**
```bash
python ad-enum-exploit.py --domain lab.local --dc 192.168.1.100 --full-enum
```
- ✅ Enumera usuários, grupos, máquinas
- ✅ Identifica usuários com SPN (Kerberoasting)
- ✅ Detecta ASREPRoasting (sem pré-autenticação)
- ✅ Password spray com delay
- ✅ Exporta relatório JSON

**Tempo economizado:** 2+ horas por engagement

---

### **2. subdomain-enum.py** (Python)
**Subdomain Enumeration + HTTP Service Discovery**
```bash
python subdomain-enum.py -d example.com --fuzzing --threads 10
```
- ✅ Combina Subfinder, Assetfinder, Amass
- ✅ Fuzzing de subdomínios comuns
- ✅ Resolve IPs paralelo
- ✅ Detecta HTTP/HTTPS + WAF
- ✅ Screenshot automático

**Tempo economizado:** 2-3 horas por reconhecimento

---

### **3. event-log-parser.ps1** (PowerShell)
**Windows Event Log Analysis - Threat Hunting**
```powershell
.\event-log-parser.ps1 -LogName Security -Hours 48 -All
```
- ✅ Analisa Security, System, Application logs
- ✅ Detecta Pass-the-Hash
- ✅ Identifica Kerberoasting
- ✅ Procura por scheduled tasks suspeitas
- ✅ Encontra processos anômalos

**Tempo economizado:** 1-2 horas de hunting manual

---

### **4. s3-bucket-enum.py** (Python)
**AWS S3 Bucket Enumeration & Exploitation**
```bash
python s3-bucket-enum.py -d example.com --fuzzing --download
```
- ✅ Descoberta de buckets por DNS
- ✅ Fuzzing de nomes
- ✅ Teste de ACL (público vs privado)
- ✅ Enumera conteúdo
- ✅ Detecta misconfigurações

**Tempo economizado:** 30+ minutos por alvo

---

### **5. sqli-waf-bypass.py** (Python)
**SQLi WAF Bypass**
```bash
python sqli-waf-bypass.py -u "http://example.com/search?q=" -p id --detect-waf
```
- ✅ Gera 50+ variações de payload
- ✅ Bypass de WAF (case, comment variants, encoding)
- ✅ Detecção automática de WAF
- ✅ Time-based e error-based detection

**Tempo economizado:** 1+ hora por teste

---

### **6. port-scan-parallel.sh** (Bash)
**Port Scan Parallelizado - Masscan + Nmap**
```bash
./port-scan-parallel.sh -t 192.168.0.0/24 --service-detection --aggressive
```
- ✅ Masscan para descoberta rápida
- ✅ Nmap paralelo para detalhes
- ✅ Detecção de serviço (-sV)
- ✅ Relatório automático

**Tempo economizado:** 30+ minutos

---

### **7. osint-api-wrapper.py** (Python)
**OSINT - Shodan, VirusTotal, CT Logs**
```bash
python osint-api-wrapper.py --full-recon example.com -o recon.json
```
- ✅ Busca Shodan por IP/hostname
- ✅ VirusTotal para reputação
- ✅ Certificate Transparency logs
- ✅ Enumeração DNS completa

**Requer API keys:** `SHODAN_API_KEY`, `VT_API_KEY`

---

### **8. credential-stuffing.py** (Python)
**Credential Stuffing contra múltiplos serviços**
```bash
python credential-stuffing.py -c user:pass -s github,aws,azure,google
```
- ✅ Testa SSH, RDP, GitHub, AWS, Azure, Google, O365
- ✅ Execução paralela
- ✅ Detecta credenciais válidas
- ✅ Exporta resultados

---

### **9. google-dorks.py** (Python)
**Automated Google Dorks**
```bash
python google-dorks.py -d example.com --all -o dorks_results.json
```
- ✅ Busca arquivos expostos
- ✅ Procura API keys
- ✅ Backups e configs
- ✅ Painéis admin

**Categorias:**
- exposed_files
- api_keys
- backup_files
- admin_panels
- credentials
- source_code
- logs

---

### **10. ssl-cert-analyzer.sh** (Bash)
**SSL Certificate Analysis + CT Logs**
```bash
./ssl-cert-analyzer.sh -d example.com --ct-logs
```
- ✅ Extrai dados do certificado
- ✅ Identifica subdomínios (SANs)
- ✅ Verifica expiração
- ✅ Extrai CT logs automático

---

### **11. ldap-injection.py** (Python)
**LDAP Injection Tester**
```bash
python ldap-injection.py -u "http://example.com/search?user=" -p username
```
- ✅ Wildcard bypass
- ✅ Boolean-based LDAP injection
- ✅ Time-based LDAP injection
- ✅ Schema inference

---

### **12. xxe-ssrf-payloader.py** (Python)
**XXE & SSRF Payloader**
```bash
python xxe-ssrf-payloader.py -u "http://example.com/api" -t both
```
- ✅ XXE file read
- ✅ Blind XXE (OOB)
- ✅ SSRF (localhost, AWS metadata, Azure, etc)
- ✅ Detecção automática

---

### **POWERSHELL SCRIPTS (6)**

### **10. event-log-parser.ps1** (PowerShell)
**Windows Registry Extraction**
```powershell
.\registry-dump.ps1 -FullDump
```
- ✅ Extrai SAM (hashes NTLM)
- ✅ RDP settings
- ✅ Browsers (Chrome, Firefox, Edge)
- ✅ Aplicações (PuTTY, VNC)
- ✅ Credenciais armazenadas

---

## 🚀 Instalação & Dependências

### Python Scripts
```bash
pip install requests dnspython paramiko boto3 shodan
```

### PowerShell Scripts
- Windows 5.1+ com privilégios administrativos
- OpenSSL para análise de certificados (bash)

### Bash Scripts
```bash
sudo apt-get install masscan nmap curl jq
```

---

## 🎯 Casos de Uso Reais

### **Pentest Externo (Reconhecimento)**
```bash
# 1. Subdomain enumeration
python subdomain-enum.py -d target.com --fuzzing

# 2. Port scanning
./port-scan-parallel.sh -t <ips_resolved>

# 3. OSINT
python osint-api-wrapper.py --full-recon target.com

# 4. Google dorks
python google-dorks.py -d target.com --all

# 5. SSL analysis
./ssl-cert-analyzer.sh -d target.com
```

### **Pentest Interno (Pós-Exploração)**
```bash
# 1. AD enumeration
python ad-enum-exploit.py --domain corp.local --full-enum

# 2. Event log analysis
.\event-log-parser.ps1 -LogName Security -All

# 3. Registry extraction
.\registry-dump.ps1 -FullDump

# 4. S3 bucket enumeration
python s3-bucket-enum.py -d corp.com --fuzzing
```

### **Threat Hunting**
```bash
# 1. Event logs
.\event-log-parser.ps1 -Suspicious -Hours 72

# 2. Process detection
.\event-log-parser.ps1 -LateralMovement

# 3. Credencial dump detection
.\registry-dump.ps1 -SAM -RDP -Browsers
```

---

## 📊 Estimativas de Tempo

| Script | Tempo Manual | Com Script | Economia |
|--------|------------|-----------|----------|
| AD Enum | 2+ horas | 5 min | 95% |
| Subdomains | 2-3 horas | 10 min | 95% |
| Event Logs | 1-2 horas | 5 min | 95% |
| Port Scan | 30+ min | 2 min | 95% |
| SQLi Testing | 1+ hora | 10 min | 90% |
| S3 Enum | 30+ min | 3 min | 90% |
| Registry Dump | 1+ hora | 2 min | 95% |

**Total economizado por pentest:** 8-15 horas

---

## ⚙️ Configuração de APIs

### Shodan
```bash
export SHODAN_API_KEY="your_api_key"
```

### VirusTotal
```bash
export VT_API_KEY="your_api_key"
```

---

## 🔒 Boas Práticas

✅ **Sempre fazer:**
- Confirmar autorização antes de usar
- Registrar tempo de execução
- Salvar relatórios em JSON
- Usar delay em testes (evitar IDS)
- Documentar achados

❌ **Nunca fazer:**
- Usar em redes sem permissão
- Executar sem escopo definido
- Deixar rastros (logs)
- Usar credenciais reais em testes

---

## 📝 Workflow Recomendado

### **1. Reconhecimento** (Fase 1)
```bash
python subdomain-enum.py -d target.com
./port-scan-parallel.sh -t discovered_ips
./ssl-cert-analyzer.sh -d target.com
python osint-api-wrapper.py --full-recon target.com
```

### **2. Enumeração** (Fase 2)
```bash
# Se AD:
python ad-enum-exploit.py --domain target.local --full-enum

# Se Web:
python sqli-waf-bypass.py -u discovered_app -p parameter
python xxe-ssrf-payloader.py -u discovered_app
```

### **3. Exploitation** (Fase 3)
```bash
# Pós-compromisso:
.\event-log-parser.ps1 -All
.\registry-dump.ps1 -FullDump
python s3-bucket-enum.py -d target.com
```

### **4. Threat Hunting** (Fase 4)
```bash
.\event-log-parser.ps1 -Suspicious -Hours 72
.\event-log-parser.ps1 -LateralMovement
```

---

## 🎓 Curva de Aprendizado

- **Iniciante:** Comece com port-scan-parallel.sh e subdomain-enum.py
- **Intermediário:** Adicione ad-enum-exploit.py e event-log-parser.ps1
- **Avançado:** Customize payloads em sqli-waf-bypass.py e xxe-ssrf-payloader.py

---

## 💡 Tips & Tricks

1. **Paralelização:** Quase todos os scripts suportam `--threads`
2. **Relatórios:** Use `-o output.json` para exportar
3. **Rate limiting:** Configure `--delay` para evitar IDS
4. **Verbose mode:** Use `-v` ou `--verbose` para debug
5. **API keys:** Exporte como variáveis de ambiente para segurança

---

## 📞 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Permission denied" (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Connection refused" (port scanning)
```bash
# Masscan precisa de privilégios root
sudo ./port-scan-parallel.sh -t target
```

---

## 🚀 Próximos Scripts Sugeridos

- [ ] Process Injection Detector (PS)
- [ ] Mimikatz Automation (PS)
- [ ] Proxy Auto-Rotation (Python)
- [ ] Scheduled Tasks Backdoor (PS)
- [ ] Automated Vuln Scanner (Python)

---

## 📄 Licença

**Apenas para fins educacionais e testes autorizados.**

---

**Desenvolvido para Red Team & Pentest especialistas | 2026**
