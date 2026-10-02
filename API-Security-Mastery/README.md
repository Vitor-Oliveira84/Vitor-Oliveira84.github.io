# 🔐 API SECURITY MASTERY

Guia profundo em segurança de APIs com 250+ payloads, técnicas avançadas para GraphQL/gRPC/WebSocket, e 6 scripts de automação

---

## 📚 DOCUMENTAÇÃO COMPLETA

### 1. **OWASP API Top 10**
- 10 vulnerabilidades fundamentais em APIs
- Teste com Burp Suite passo-a-passo
- BOLA (IDOR) em APIs
- Broken Authentication
- Excessive Data Exposure
- Rate Limiting
- Broken Function Authorization
- Mass Assignment
- Security Misconfiguration
- Injection (SQL, Command)
- Improper Assets Management
- Insufficient Logging

👉 [02-OWASP-API-TOP-10-DETALHADO.md](02-OWASP-API-TOP-10-DETALHADO.md)

### 2. **Técnicas Avançadas** 
Arquiteturas modernas:
- **GraphQL** - Introspection, N+1 Attack, Query Complexity, Auth Bypass
- **gRPC** - Reflection, Unencrypted Traffic, Missing Auth
- **WebSocket** - Unvalidated Messages, CSRF, XSS
- **OAuth 2.0** - Redirect URI Bypass, Missing State, Token Reuse
- **JWT** - Algorithm Confusion, Secret Bruteforce
- **Webhooks** - SSRF, Timing Attacks

👉 [03-TECNICAS-AVANCADAS-APIS.md](03-TECNICAS-AVANCADAS-APIS.md)

### 3. **Burp Suite para APIs** ⭐ NOVO
Configuração completa:
- Setup Proxy (127.0.0.1:8080)
- Repeater - testes manuais
- Intruder - fuzzing e enumeração
- Decoder - análise de tokens
- Comparer - análise de respostas
- Scanner - testes automáticos
- Macros - autenticação automática
- Extensions avançadas

👉 [04-BURP-SUITE-PARA-APIS.md](04-BURP-SUITE-PARA-APIS.md)

### 4. **Payload Database** ⭐ NOVO
250+ payloads para:
- **REST** (50+) - BOLA, Auth bypass, Parameter fuzzing
- **SQL Injection** (40+) - Union-based, Blind, Time-based
- **Command Injection** (30+) - Shell, Blind exfiltration
- **XXE** (25+) - File reading, Blind XXE, OOB
- **SSTI** (30+) - Jinja2, Velocity, FreeMarker
- **GraphQL** (35+) - Introspection, N+1, DoS
- **WebSocket** (20+) - Unvalidated, CSRF, XSS
- **OAuth** (20+) - Redirect bypass, State bypass
- **JWT** (25+) - Algorithm confusion, Claims
- **CORS** (15+) - Wildcard, Credentials
- **SSRF** (20+) - Localhost, AWS metadata, Port scanning

👉 [05-PAYLOAD-DATABASE-APIS.md](05-PAYLOAD-DATABASE-APIS.md)

### 5. **Reconnaissance** ⭐ NOVO
Descoberta e mapeamento:
- Google Dorks para APIs
- Padrões comuns (/api, /graphql, etc)
- Browser DevTools analysis
- Burp Suite HTTP History
- FFUF para endpoint discovery
- Swagger/OpenAPI enumeration
- GraphQL Introspection
- Versão enumeration (/v1, /v2, etc)
- Rate limit detection
- Authentication testing
- Documentação template

👉 [06-RECON-ENUMERATION-APIS.md](06-RECON-ENUMERATION-APIS.md)

### 6. **Scripts de Automação** ⭐ NOVO
6 scripts prontos para usar:

1. **discover-api.py** - Descoberta automática de endpoints
2. **bola-tester.py** - BOLA/IDOR testing automático
3. **jwt-bruteforce.py** - Análise e bruteforce de JWT
4. **sqli-tester.py** - SQL Injection testing
5. **rate-limit-bypass.py** - Teste de rate limit
6. **graphql-introspect.py** - Extrator de schema GraphQL

👉 [07-SCRIPTS-AUTOMACAO-APIS.md](07-SCRIPTS-AUTOMACAO-APIS.md)

---

## 📊 ESTATÍSTICAS

| Métrica | Valor |
|---|---|
| **Linhas de conteúdo** | 5,500+ |
| **Documentos** | 6 |
| **Vulnerabilidades** | 20+ |
| **Payloads** | 250+ |
| **Scripts prontos** | 6 |
| **Técnicas avançadas** | 6 arquiteturas |
| **Recompensa potencial** | $500-15K/bug |
| **CVSS médio** | 8.0 |

---

## 🎯 VULNERABILIDADES POR SEVERIDADE

### CRÍTICO (9.0-10.0)
- GraphQL Introspection + N+1
- JWT Algorithm Confusion
- Webhook SSRF
- SQL Injection em APIs
- Command Injection

### ALTO (7.0-8.9)
- BOLA/IDOR
- Broken Authentication
- Excessive Data Exposure
- gRPC Reflection
- OAuth Redirect Bypass

### MÉDIO (4.0-6.9)
- Rate Limiting Bypass
- WebSocket CSRF
- CORS Misconfiguration
- Improper Assets Management

---

## 💰 RECOMPENSA POTENCIAL

| Vulnerabilidade | Min | Max | Tempo |
|---|---|---|---|
| BOLA | $500 | $5K | 30min-2h |
| Broken Auth | $1K | $10K | 1-4h |
| GraphQL Injection | $500 | $5K | 1-2h |
| JWT Exploit | $2K | $10K | 1.5h |
| OAuth Bypass | $5K | $15K | 2-3h |
| Webhook SSRF | $2K | $10K | 1h |

---

## 🎓 LEARNING PATH (8 SEMANAS)

### Semana 1-2: Fundações
- HTTP/REST basics
- API architecture
- Burp Suite setup

### Semana 3-4: OWASP API Top 10
- Testar cada vulnerabilidade
- BOLA exploitation
- Authentication testing

### Semana 5-6: Técnicas Avançadas
- GraphQL attacks
- gRPC exploitation
- JWT attacks

### Semana 7-8: Prática
- Usar scripts de automação
- Teste em APIs públicas
- Bug bounty submissions

---

## 🚀 QUICK START

```bash
# 1. Setup Burp
burpsuite &

# 2. Configurar proxy
# Proxy → Options → 127.0.0.1:8080

# 3. Descobrir endpoints
python3 07-SCRIPTS-AUTOMACAO-APIS.md # discover-api.py

# 4. Testar BOLA
python3 bola-tester.py https://api.target.com

# 5. Analisar GraphQL
python3 graphql-introspect.py https://api.target.com/graphql
```

---

## ✅ CHECKLIST

- [ ] Entende arquitetura de APIs
- [ ] Burp Suite configurado
- [ ] OWASP API Top 10 memorizado
- [ ] Testou GraphQL Introspection
- [ ] Testou BOLA em uma API
- [ ] JWT bruteforce bem-sucedido
- [ ] Rate limit bypass explorado
- [ ] Webhook SSRF testado
- [ ] Scripts de automação funcionando
- [ ] Primeira vulnerabilidade encontrada

---

## 🔗 RECURSOS

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [API Hacking Book](https://www.amazon.com/API-Hacking-Exposed-vulnerabilities-exploitation-ebook/dp/B095SLQSRD)
- [PortSwigger GraphQL](https://portswigger.net/web-security/graphql)
- [HackerOne Reports](https://hackerone.com/reports)

---

## 🤖 Gerado com Claude Code
Este guia foi criado com a ajuda de AI para garantir precisão técnica e cobertura completa.

**Status:** ✅ Completo | **Última atualização:** 2026-10-02 | **Versão:** 1.0
