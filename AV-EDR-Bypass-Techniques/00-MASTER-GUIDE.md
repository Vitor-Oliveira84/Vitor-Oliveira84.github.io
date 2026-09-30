# Endpoint Protection Evasion - Complete Technical Guide

**Disclaimer:** Este documento é destinado exclusivamente para fins educacionais e pesquisa de segurança em ambientes autorizados. Todas as técnicas descritas devem ser utilizadas apenas em testes de segurança autorizados (pentest, red team) em ambientes controlados.

---

## 📋 Índice Geral

### Módulo 1: Fundamentos de Evasão de Antivírus
- Estrutura Portable Executable (PE)
- Windows APIs e System Calls
- P/Invoke vs D/Invoke
- Detecção por Assinatura
- Shellcode Runners & Crypters
- Detecção Heurística/Comportamental
- Técnicas de Reflection
- Evasão em Linux
- EDR (Endpoint Detection & Response)
- Hells Gate e System Call Obfuscation

### Módulo 2: Técnicas de Injeção de Código
- Process Injection (múltiplas variantes)
- Process Hollowing
- DLL Injection
- DLL Sideloading (Supply Chain)
- Backdooring de Binários

### Módulo 3-4: Command & Control + Windows Security Controls
- C2 Redirectors
- Network Profiles (Malleable C2)
- Covert Channels
- Domain Fronting
- HTML Smuggling
- AppLocker e Bypasses
- LAPS (Local Administrator Password Solution)
- PPL (Protected Processes Light)
- ETW (Event Tracing for Windows)
- Sysmon
- Binary Signing & Code Certificates
- Mark of the Web (SmartScreen)

### Módulo 5: Macros & Entrega de Payload
- VBA (Visual Basic Application)
- Técnicas de AutoOpen
- Execução via Shell/WSH
- WMI Dechaining
- Ofuscação de VBA
- VBA Stomping
- Phishing com LNK Files

---

## 🎯 Estrutura da Documentação

Cada técnica inclui:
1. **Conceito:** Explicação teórica
2. **Como funciona:** Detalhamento técnico
3. **Implementação:** Passos práticos
4. **Detecção:** Como defenders identificam
5. **Mitigação:** Como se proteger
6. **Exemplos de código** (quando aplicável)

---

## ⚠️ Avisos Importantes

- Todas as técnicas são aplicáveis apenas em **ambientes autorizados**
- Respeite as leis locais e regulamentações sobre segurança
- Obtenha autorização escrita antes de qualquer teste
- Use em laboratórios ou ambientes de teste
- Não aplique em sistemas de terceiros sem consentimento explícito

---

## 📚 Como Usar Este Guia

1. Comece pelos fundamentos (Módulo 1)
2. Progrida para técnicas avançadas
3. Implemente em ambiente de laboratório
4. Teste contra soluções de segurança
5. Documente comportamentos e IOCs (Indicators of Compromise)
6. Adapte técnicas para seu cenário específico

---

**Última atualização:** 2026-09-30  
**Status:** Documentação Técnica Completa  
**Propósito:** Pesquisa e Educação de Segurança Ofensiva
