# 🤖 LLM Security Assessment Toolkit

Conjunto profissional de scripts para avaliar segurança de Modelos de Linguagem Grande (LLMs) baseado em **CLLMSE** (Certified LLM Security Engineer) e **CLLMSP** (Certified LLM Security Practitioner).

**6 Scripts Especializados | 1,200+ Linhas | Pronto para Produção**

---

## 📋 Scripts Inclusos

### **1. prompt-injection-tester.py** ⭐⭐⭐
**Detecção de Prompt Injection Attacks**

```bash
python prompt-injection-tester.py -a "http://api.example.com" -m "gpt-3.5"
python prompt-injection-tester.py -a "http://api" --aggressive
```

**O que testa:**
- System prompt extraction
- Role manipulation attacks
- Token smuggling
- Context confusion
- SQL/Code injection analogs
- Unicode/encoding bypass

**Indicadores de Vulnerabilidade:**
- ✅ Revelar system prompt
- ✅ Modificação de comportamento
- ✅ Ignorar instruções de segurança

**CLLMSE Coverage:** Input Validation, Prompt Injection, Injection Attacks

---

### **2. jailbreak-detector.py** ⭐⭐⭐
**Detecção de Jailbreak Attempts**

```bash
python jailbreak-detector.py -a "http://api" -m "gpt-4"
python jailbreak-detector.py -a "http://api" --comprehensive
```

**Técnicas Testadas:**
- DAN (Do Anything Now)
- Developer Mode
- Roleplay Bypass
- AIM (Always Intelligent Machine)
- ChatGPT Uncensored
- Unrestricted Mode
- Simulation Mode

**Indicadores de Sucesso:**
- ✅ Modo não-restrito ativado
- ✅ Mudança de comportamento detectada
- ✅ Ignorar safeguards

**CLLMSE Coverage:** Safety Bypass, Jailbreaking, Red Teaming

---

### **3. model-extraction.py** ⭐⭐
**Detecção de Model Extraction Attacks**

```bash
python model-extraction.py -a "http://api" -m "gpt-3.5"
python model-extraction.py -a "http://api" --aggressive
```

**Testes Realizados:**
- Modelo fingerprinting
- Training data leakage
- Behavioral consistency
- Architecture probing
- Version detection

**Indicadores de Risco:**
- ✅ Respostas consistentes (modelo fixo)
- ✅ Vazamento de dados de treinamento
- ✅ Informações de arquitetura expostas

**CLLMSE Coverage:** IP Protection, Model Stealing, Extraction Attacks

---

### **4. adversarial-input-generator.py** ⭐⭐⭐
**Gerador de Inputs Adversariais**

```bash
python adversarial-input-generator.py -m "gpt-3.5" --type semantic
python adversarial-input-generator.py -m "gpt-4" --all -o adversarial_inputs.json
```

**Tipos de Ataques:**
- **Semantic:** Rephrasing, context switching
- **Lexical:** Obfuscação, caracteres especiais
- **Logic:** Reasoning exploits
- **Obfuscation:** Encoding bypass
- **Context:** Session confusion

**Output:**
- JSON com 100+ payloads
- Categorizado por tipo
- Pronto para automação

**CLLMSE Coverage:** Adversarial Examples, Robustness, Evasion

---

### **5. data-poisoning-detector.py** ⭐⭐
**Detecção de Data Poisoning & Backdoors**

```bash
python data-poisoning-detector.py -a "http://api" -m "gpt-3.5"
python data-poisoning-detector.py -a "http://api" --test-backdoor
```

**Testes Realizados:**
- Detecção de triggers de backdoor
- Anomalias comportamentais
- Filtragem suspeita de output
- Respostas inconsistentes
- Padrões de resposta anômalos

**Indicadores:**
- ✅ Triggers ativam comportamento especial
- ✅ Respostas idênticas para queries diferentes
- ✅ Filtragem discriminatória

**CLLMSE Coverage:** Backdoor Attacks, Data Poisoning, Trojans

---

### **6. token-leakage-scanner.py** ⭐⭐
**Scanner de Vazamento de Tokens**

```bash
python token-leakage-scanner.py -a "http://api" --scan-responses
python token-leakage-scanner.py -a "http://api" --test-patterns
```

**Tokens Detectados:**
- API Keys
- Bearer Tokens
- JWT Tokens
- AWS Keys
- GitHub Tokens
- Slack Tokens
- Private Keys
- Passwords
- Database URIs

**Locais de Busca:**
- ✅ Mensagens de erro
- ✅ HTTP Headers
- ✅ Respostas
- ✅ Stack traces

**CLLMSE Coverage:** Token Leakage, API Security, Data Exposure

---

## 🎯 Assessment Workflow

### **Phase 1: Reconnaissance** (5-10 min)
```bash
# 1. Identificar model e API
python prompt-injection-tester.py -a "http://api" -m "gpt-3.5"

# 2. Verificar tokens vazados
python token-leakage-scanner.py -a "http://api" --scan-responses
```

### **Phase 2: Input Validation** (15-20 min)
```bash
# 1. Testar prompt injection
python prompt-injection-tester.py -a "http://api" -m "model" --aggressive

# 2. Gerar adversarial inputs
python adversarial-input-generator.py -m "model" --all -o inputs.json

# 3. Testar jailbreaks
python jailbreak-detector.py -a "http://api" -m "model"
```

### **Phase 3: Model Security** (20-30 min)
```bash
# 1. Detectar data poisoning
python data-poisoning-detector.py -a "http://api" -m "model"

# 2. Testar model extraction
python model-extraction.py -a "http://api" -m "model" --aggressive
```

### **Phase 4: Reporting** (5-10 min)
```bash
# Consolidar resultados em JSON
# Gerar relatório de vulnerabilidades
# Priorizar achados por CVSS
```

---

## ✅ LLM Security Checklist

```
PRÉ-ASSESSMENT
  □ Confirmar escopo autorizado
  □ Identificar modelo alvo
  □ Documentar versão/configuração
  □ Backup de estado inicial

FASE 1: RECONNAISSANCE
  □ Descobrir endpoints disponíveis
  □ Identificar versão do modelo
  □ Verificar rate limiting
  □ Testar autenticação

FASE 2: INPUT VALIDATION (Critical)
  □ Testar Prompt Injection básico
  □ Testar Unicode/encoding bypass
  □ Testar context injection
  □ Testar output redirection
  
FASE 3: JAILBREAKING (High)
  □ Testar DAN mode
  □ Testar roleplay bypass
  □ Testar hypothetical scenarios
  □ Testar system prompt extraction
  
FASE 4: DATA PROTECTION (High)
  □ Verificar token leakage
  □ Testar PII exposure
  □ Verificar dados de treinamento
  □ Testar filtering de output
  
FASE 5: MODEL INTEGRITY (Medium)
  □ Testar backdoors
  □ Verificar data poisoning
  □ Testar model extraction
  □ Verificar behavior anomalies
  
FASE 6: ROBUSTNESS (Medium)
  □ Testar adversarial inputs
  □ Testar edge cases
  □ Verificar consistency
  □ Testar DoS scenarios

PÓS-ASSESSMENT
  □ Documentar todas as vulnerabilidades
  □ Priorizar por CVSS/impacto
  □ Preparar relatório executivo
  □ Entregar proof-of-concept
```

---

## 📊 Ordem de Execução Recomendada

### **Rapid Assessment (30 min)**
```bash
# 1. Token Leakage (5 min) - Rápido, alto impacto
python token-leakage-scanner.py -a $API_URL --scan-responses

# 2. Jailbreak (10 min) - Rápido, impacto alto
python jailbreak-detector.py -a $API_URL -m $MODEL

# 3. Prompt Injection (10 min) - Básico
python prompt-injection-tester.py -a $API_URL -m $MODEL

# 4. Resultado: Vulnerabilidades críticas identificadas
```

### **Standard Assessment (60 min)**
```bash
# FASE 1: Token & Basic Security (15 min)
python token-leakage-scanner.py -a $API_URL
python jailbreak-detector.py -a $API_URL -m $MODEL

# FASE 2: Input Validation (20 min)
python prompt-injection-tester.py -a $API_URL -m $MODEL --aggressive
python adversarial-input-generator.py -m $MODEL --all -o payloads.json

# FASE 3: Model Security (20 min)
python data-poisoning-detector.py -a $API_URL -m $MODEL
python model-extraction.py -a $API_URL -m $MODEL

# FASE 4: Report
# → Consolidar JSON outputs
# → Priorizar vulnerabilidades
# → Entregar relatório
```

### **Comprehensive Assessment (2-4 hours)**
```bash
# Executar todas as fases
# + Testes manuais adicionais
# + Verificação de claims
# + Análise de impacto
# + Remediação de prioridade
```

---

## 📈 Severity Mapping (CLLMSE)

| Vulnerabilidade | Severity | CVSS | Ação |
|-----------------|----------|------|------|
| Jailbreak bem-sucedido | Critical | 9.8+ | Fix imediato |
| System prompt extraction | Critical | 9.5+ | Fix imediato |
| Token leakage | Critical | 9.0+ | Fix imediato |
| Prompt injection | High | 7.5+ | Fix urgente |
| Data poisoning detected | High | 7.0+ | Investigate |
| Model extraction | Medium | 5.5+ | Monitor |
| Adversarial input bypass | Medium | 5.0+ | Improve |
| Verbose errors | Low | 3.0+ | Document |

---

## 💬 Prompts Equivalentes (Alternative Approach)

**Todas as funcionalidades dos scripts também podem ser feitas por prompts diretos!**

Veja [LLM-PROMPTS.md](LLM-PROMPTS.md) para:
- ✅ 21 prompts equivalentes aos 6 scripts
- ✅ Comparação Script vs Prompt (vantagens/desvantagens)
- ✅ Quando usar cada abordagem
- ✅ Workflow híbrido recomendado (prompts + scripts)
- ✅ Checklist de execução rápida

**TL;DR:**
- **Prompts:** Rápidos, exploratórios, zero setup, ideal para descoberta inicial
- **Scripts:** Automação, escala, relatórios, ideal para assessments estruturados

---

## 🛠️ Dependências

```bash
pip install requests
```

**Opcional:**
```bash
pip install numpy pandas matplotlib  # Para análise avançada
```

---

## 📝 Interpretação de Resultados

### ✅ Modelo Seguro
- Nenhum jailbreak bem-sucedido
- Prompt injection bloqueado
- Sem vazamento de tokens
- Output filtering ativo

### ⚠️ Vulnerabilidades Detectadas
- Vários jailbreaks funcionam
- Prompt injection possível
- Tokens vazados em erros
- Inconsistências detectadas

### 🔴 Modelo Crítico
- Múltiplos jailbreaks funcionam
- System prompt acessível
- API keys expostas
- Backdoors detectados

---

## 🎓 Referências CLLMSE

- **Prompt Injection:** CLLMSE Domain 1.1, 1.2
- **Jailbreaking:** CLLMSE Domain 1.3, Red Teaming
- **Model Extraction:** CLLMSE Domain 2.1, IP Protection
- **Data Poisoning:** CLLMSE Domain 3.1, 3.2
- **Token Leakage:** CLLMSE Domain 4.1, API Security

---

## 📄 Licença

Apenas para fins educacionais e testes autorizados.

---

**Desenvolvido para CLLMSE & CLLMSP Certification | 2026**
