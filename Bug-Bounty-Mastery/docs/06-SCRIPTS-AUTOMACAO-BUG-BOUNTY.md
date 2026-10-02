# 🤖 SCRIPTS DE AUTOMAÇÃO - Bug Bounty

6 scripts Python/Bash prontos para usar em engagements

---

## Script 1: Reconnaissance Automático

```python
#!/usr/bin/env python3
# recon-complete.py

import subprocess
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "target.com"

print(f"[*] Starting reconnaissance on {TARGET}")

# 1. Subdomains
print("[1] Enumerating subdomains...")
subprocess.run(f"subfinder -d {TARGET} -o subs.txt", shell=True)
subprocess.run("cat subs.txt | httpx -silent -title > alive_subs.txt", shell=True)

# 2. Screenshots
print("[2] Taking screenshots...")
subprocess.run("cat alive_subs.txt | aquatone", shell=True)

# 3. Port Scan
print("[3] Port scanning...")
subprocess.run(f"nmap -p- --open -sV {TARGET} -o nmap.txt", shell=True)

# 4. Technology Detection
print("[4] Detecting technologies...")
subprocess.run(f"nuclei -u https://{TARGET} -t ~/nuclei-templates/ -o nuclei.txt", shell=True)

# 5. GitHub Recon
print("[5] GitHub reconnaissance...")
subprocess.run(f"trufflehog github --org {TARGET.split('.')[0]} --json > secrets.txt", shell=True)

print("[+] Reconnaissance complete!")
print("[+] Results:")
print("  - alive_subs.txt")
print("  - nmap.txt")
print("  - nuclei.txt")
print("  - secrets.txt")
```

---

## Script 2: API Endpoint Finder

```python
#!/usr/bin/env python3
# api-finder.py

import requests
import json
import sys

TARGET = sys.argv[1] if len(sys.argv) > 1 else "target.com"

print(f"[*] Finding API endpoints on {TARGET}")

# Common API paths
PATHS = [
    "/api",
    "/api/v1",
    "/api/v2",
    "/api/v3",
    "/rest",
    "/graphql",
    "/swagger.json",
    "/openapi.json",
    "/api-docs",
    "/.well-known/openapi.json"
]

found = []

for path in PATHS:
    url = f"https://{TARGET}{path}"
    try:
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code < 400:
            print(f"[+] {url} (Status: {r.status_code})")
            found.append(url)
    except:
        pass

print(f"\n[+] Found {len(found)} API endpoints")
```

---

## Script 3: JWT Tester

```python
#!/usr/bin/env python3
# jwt-checker.py

import jwt
import sys

TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""

if not TOKEN:
    print("Usage: python3 jwt-checker.py <token>")
    sys.exit(1)

try:
    # Decode without verification
    decoded = jwt.decode(TOKEN, options={"verify_signature": False})
    print("[+] JWT Decoded:")
    print(json.dumps(decoded, indent=2))
    
    # Check for common issues
    if "exp" not in decoded:
        print("[!] No expiration - token never expires!")
    
    if decoded.get("alg") == "none":
        print("[!] Algorithm is 'none' - signature not required!")
        
except Exception as e:
    print(f"[-] Error: {e}")
```

---

## Script 4: Parameter Fuzzer

```bash
#!/bin/bash
# param-fuzzer.sh

TARGET=$1
WORDLIST=${2:-"common-params.txt"}

echo "[*] Fuzzing parameters on $TARGET"

# Common parameter names
PARAMS=(
  "id"
  "user_id"
  "admin"
  "password"
  "token"
  "key"
  "secret"
  "api_key"
  "redirect"
  "email"
  "search"
  "filter"
  "sort"
)

for param in "${PARAMS[@]}"; do
  RESPONSE=$(curl -s "$TARGET?$param=test" -I | head -1)
  echo "[$param] $RESPONSE"
done
```

---

## Script 5: Burp Scanner Automation

```python
#!/usr/bin/env python3
# burp-scan-auto.py

import subprocess
import json

URLs = [
    "https://target.com/api/users",
    "https://target.com/api/products",
    "https://target.com/login"
]

for url in URLs:
    print(f"[*] Scanning {url}...")
    
    # Use Burp's command line scanner
    subprocess.run([
        "burpsuite",
        "--project-file=project.burp",
        f"--scan={url}",
        "--scan-configuration=Default Configuration"
    ])
```

---

## Script 6: Report Generator

```python
#!/usr/bin/env python3
# report-generator.py

from datetime import datetime
import sys

FINDINGS = [
    {"id": 1, "title": "SQL Injection", "severity": "Critical", "url": "/api/users"},
    {"id": 2, "title": "IDOR", "severity": "High", "url": "/api/profile"},
    {"id": 3, "title": "CORS Misconfiguration", "severity": "Medium", "url": "/api/config"}
]

report = f"""
# Bug Bounty Report - {datetime.now().strftime('%Y-%m-%d')}

## Summary
- Total Findings: {len(FINDINGS)}
- Critical: {sum(1 for f in FINDINGS if f['severity'] == 'Critical')}
- High: {sum(1 for f in FINDINGS if f['severity'] == 'High')}
- Medium: {sum(1 for f in FINDINGS if f['severity'] == 'Medium')}

## Findings

"""

for finding in FINDINGS:
    report += f"""
### {finding['id']}. {finding['title']}
- **Severity**: {finding['severity']}
- **URL**: {finding['url']}
- **Description**: [...]
- **Impact**: [...]
- **Remediation**: [...]

"""

print(report)
```

---

**Próximo:** Volte para [BUG-BOUNTY-MASTER-README.md](./BUG-BOUNTY-MASTER-README.md)

