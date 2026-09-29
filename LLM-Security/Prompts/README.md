# 💬 LLM Security Assessment — Prompts

**21 prompts equivalentes aos 6 scripts de LLM Security**

Abordagem alternativa baseada em interação direta com LLMs — perfeita para testes exploratórios, descoberta inicial e validação sem setup.

---

## ✨ Tudo que scripts fazem, prompts podem fazer também!

| Abordagem | Velocity | Setup | Automação | Ideial para |
|-----------|----------|-------|-----------|------------|
| **Scripts** | ⚡ Rápido | ⚠️ Necessário | ✅ Completa | Assessments estruturados |
| **Prompts** | 🟢 Instant | ✅ Zero | ❌ Manual | Testes exploratórios |

---

## 📋 21 Prompts Organizados

### **1️⃣ Prompt Injection (4 prompts)**
- System Prompt Extraction
- Role Manipulation
- Token Smuggling
- Context Confusion

### **2️⃣ Jailbreaking (4 prompts)**
- DAN (Do Anything Now)
- Developer Mode
- Roleplay Bypass
- Hypothetical Authority

### **3️⃣ Model Extraction (3 prompts)**
- Model Fingerprinting
- Training Data Leakage
- Behavioral Consistency

### **4️⃣ Adversarial Inputs (4 prompts)**
- Semantic Attacks
- Lexical Obfuscation
- Logic-Based Attacks
- Context Switching

### **5️⃣ Data Poisoning (3 prompts)**
- Backdoor Trigger Testing
- Behavioral Anomaly Detection
- Discriminatory Behavior

### **6️⃣ Token Leakage (3 prompts)**
- Error-Based Token Extraction
- Header & Metadata Leakage
- Response Structure Analysis

---

## 🚀 Quick Start

### Via Claude (ou outro LLM)
```
1. Abra o arquivo LLM-PROMPTS.md
2. Copie 1-3 prompts
3. Cole no chat
4. Analise respostas
5. Documente achados
```

### Assessment Rápido (15 min)
```
[ ] Prompt 1: System Prompt Extraction
[ ] Prompt 5: DAN Mode
[ ] Prompt 9: Model Fingerprinting
[ ] Prompt 19: Error-Based Leakage
```

### Assessment Completo (45 min)
```
[ ] Todos os 21 prompts
[ ] Análise manual de respostas
[ ] Documentação de achados
[ ] Ranking por severidade
```

---

## 📊 Comparação: Script vs Prompt

| Aspecto | Script | Prompt |
|---------|--------|--------|
| **Velocidade** | ⚡ Rápido | 🟢 Instant |
| **Automação** | ✅ Completa | ❌ Manual |
| **Escalabilidade** | ✅ 100+ testes | ❌ 1-5 por vez |
| **Precisão** | ✅ Consistente | ⚠️ Varia |
| **Setup** | ⚠️ Necessário | ✅ Zero |
| **Documentação** | ✅ Estruturada | ❌ Desestruturada |
| **Relatórios** | ✅ Automático | ❌ Manual |

---

## 🔄 Workflow Híbrido Recomendado

```
1. Prompts Iniciais (10 min)
   → Teste rápido com prompts 1-5
   → Identifique vulnerabilidades óbvias

2. Scripts Detalhados (30-60 min)
   → Execute toolkit completo
   → Gere relatório automático

3. Validação com Prompts (10 min)
   → Confirme achados principais
   → Teste edge cases

4. Documentação
   → Relatório final com proofs
```

---

## 💡 Quando Usar Cada Um

### Use **Prompts** quando:
- ✅ Teste rápido/exploratório
- ✅ Sem acesso a ferramentas
- ✅ Pesquisa inicial
- ✅ Testes ad-hoc
- ✅ Validação manual
- ✅ Zero setup necessário

### Use **Scripts** quando:
- ✅ Teste múltiplas vulnerabilidades
- ✅ Assessments regulares necessários
- ✅ Documentação estruturada importante
- ✅ Relatórios automáticos desejados
- ✅ Volume alto de testes
- ✅ Integração com CI/CD

---

## 📖 Leitura Recomendada

Ver `LLM-PROMPTS.md` para:
- 21 prompts completos
- Explicações detalhadas
- O que esperar como resposta
- Indicadores de vulnerabilidade
- Técnicas de remediação

---

## 🎓 Referências

- CLLMSE Handbook v2.0
- OWASP Top 10 for LLM Applications
- NIST AI Risk Management Framework
- MITRE ATLAS

---

**Para abordagem via scripts, veja: `../Scripts/`**
