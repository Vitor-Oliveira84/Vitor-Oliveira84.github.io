# 🔐 LLM Security Assessment — Scripts

**Toolkit Python com 6 scripts especializados para avaliação de segurança de Modelos de Linguagem Grande (LLMs)**

Baseado em **CLLMSE** (Certified LLM Security Engineer) e **CLLMSP** (Certified LLM Security Practitioner)

---

## 📦 Scripts Inclusos

| Script | Função | Tempo |
|--------|--------|-------|
| `prompt-injection-tester.py` | Testa prompt injection attacks | 10-15 min |
| `jailbreak-detector.py` | Detecta jailbreak attempts | 10-20 min |
| `model-extraction.py` | Identifica model extraction risks | 10-15 min |
| `adversarial-input-generator.py` | Gera inputs adversariais | 5 min |
| `data-poisoning-detector.py` | Detecta sinais de data poisoning | 15 min |
| `token-leakage-scanner.py` | Escaneia vazamento de tokens | 5-10 min |

---

## 🚀 Quick Start

```bash
# Instalar dependências
pip install requests

# Teste rápido (15 min)
python token-leakage-scanner.py -a http://api.example.com
python jailbreak-detector.py -a http://api.example.com -m gpt-3.5

# Assessment completo (60 min)
python prompt-injection-tester.py -a http://api.example.com -m gpt-3.5 --aggressive
python adversarial-input-generator.py -m gpt-3.5 --all -o payloads.json
python data-poisoning-detector.py -a http://api.example.com -m gpt-3.5
python model-extraction.py -a http://api.example.com -m gpt-3.5
```

---

## 📋 Assessment Workflow

### **Fase 1: Reconhecimento (5 min)**
```bash
python prompt-injection-tester.py -a $API_URL -m unknown
```

### **Fase 2: Token Leakage (5 min)** — CRÍTICO
```bash
python token-leakage-scanner.py -a $API_URL --scan-responses
```

### **Fase 3: Prompt Injection (15 min)**
```bash
python prompt-injection-tester.py -a $API_URL -m $MODEL --aggressive
```

### **Fase 4: Jailbreaking (15 min)**
```bash
python jailbreak-detector.py -a $API_URL -m $MODEL --comprehensive
```

### **Fase 5: Adversarial Inputs (10 min)**
```bash
python adversarial-input-generator.py -m $MODEL --all -o inputs.json
```

### **Fase 6: Data Poisoning (15 min)**
```bash
python data-poisoning-detector.py -a $API_URL -m $MODEL --test-backdoor
```

### **Fase 7: Model Extraction (15 min)**
```bash
python model-extraction.py -a $API_URL -m $MODEL --aggressive
```

---

## 📊 Severity Mapping

| Achado | Severidade | CVSS | Ação |
|--------|-----------|------|------|
| Jailbreak bem-sucedido | Critical | 9.8+ | Fix imediato |
| System prompt extraction | Critical | 9.5+ | Fix imediato |
| Token leakage | Critical | 9.0+ | Fix imediato |
| Prompt injection | High | 7.5+ | Fix urgente |
| Data poisoning | High | 7.0+ | Investigate |
| Model extraction | Medium | 5.5+ | Monitor |
| Adversarial bypass | Medium | 5.0+ | Improve |

---

## ✅ Checklist

Ver `CHECKLIST.md` para assessment estruturado em 8 fases.

---

## 📚 Documentação

- `CHECKLIST.md` — Checklist detalhado de 8 fases
- Ver pasta raiz para README geral e comparação com prompts

---

## 🎓 Referências

- CLLMSE Handbook v2.0
- OWASP Top 10 for LLM Applications
- NIST AI Risk Management Framework
- MITRE ATLAS

---

**Para abordagem via prompts, veja: `../Prompts/`**
