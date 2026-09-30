# Endpoint Protection Evasion - Comprehensive Technical Guide

> **⚠️ DISCLAIMER:** This documentation is for educational purposes and authorized security testing only. Unauthorized access to computer systems is illegal.

---

## 📑 Documentation Structure

Complete technical documentation across 5 modules covering endpoint protection evasion techniques.

### Files in This Repository

- **`00-MASTER-GUIDE.md`** - Overview and roadmap
- **`01-ANTIVIRUS-FUNDAMENTALS.md`** - PE, APIs, D/Invoke, shellcode, EDR
- **`02-CODE-INJECTION-TECHNIQUES.md`** - Process injection, hollowing, DLL injection
- **`03-C2-AND-WINDOWS-CONTROLS.md`** - C2, AppLocker, LAPS, PPL, ETW, Sysmon
- **`04-MACROS-AND-PAYLOAD-DELIVERY.md`** - VBA, macros, LNK phishing, CPL

---

## 🎯 Quick Start

1. Start with `00-MASTER-GUIDE.md`
2. Progress through modules sequentially
3. Complete lab exercises for each module
4. Test in isolated environment
5. Document results

---

## 📚 What You'll Learn

✅ Windows PE structure and internals
✅ Windows APIs (Win32, NT APIs, syscalls)
✅ Antivirus signature evasion
✅ Behavioral/heuristic evasion
✅ Process injection (5+ techniques)
✅ EDR bypass techniques
✅ C2 infrastructure setup
✅ AppLocker bypass (8+ methods)
✅ Macro development & obfuscation
✅ Complete attack chains

---

## 📊 Techniques Covered

- PE structure, APIs, D/Invoke, shellcode, EDR basics
- Process injection, hollowing, DLL injection, sideloading
- C2 redirectors, AppLocker bypasses, LAPS, PPL, ETW, Sysmon
- VBA development, macro obfuscation, LNK phishing, CPL files

---

## 📑 Complete Table of Contents

### Módulo 1: Fundamentos de Evasão de Antivírus
- Estrutura Portable Executable (PE)
- Windows APIs e System Calls
- P/Invoke vs D/Invoke
- Detecção por Assinatura
- Shellcode Runners & Crypters
- Detecção Heurística/Comportamental
- Reflection
- Evasão em Linux
- EDR (Endpoint Detection & Response)
- Hells Gate & System Call Obfuscation

### Módulo 2: Técnicas de Injeção de Código
- Classic Process Injection
- NtMapViewOfSection Injection
- QueueUserAPC Injection
- Process Hollowing (RunPE)
- DLL Injection (Disk-Based)
- Reflective DLL Injection
- Shellcode RDI (sRDI)
- DLL Sideloading
- Backdooring de Binários

### Módulo 3-4: Command & Control + Windows Security Controls
**Parte 1: C2 Evasion**
- C2 Redirectors
- Network Profiles (Malleable C2)
- Covert Channels
- Domain Fronting
- HTML Smuggling

**Parte 2: Windows Security Controls**
- AppLocker (Fundamentals & 8+ Bypasses)
- LAPS (Local Administrator Password Solution)
- PPL (Protected Processes Light)
- ETW (Event Tracing for Windows)
- Sysmon
- Binary Signing & Code Certificates
- Mark of the Web (SmartScreen)

### Módulo 4: Macros e Entrega de Payload
- VBA Fundamentals
- Macro AutoOpen & Obfuscation
- Técnicas de Execução (Shell, WScript, WMI, Shellcode)
- VBA Stomping (EvilClippy)
- Phishing com LNK Files
- CPL Files (Control Panel)
- Análise Forense e IOCs

---

## 🛡️ Defensive Perspective

Each module includes:
- Detection methods
- Indicators of Compromise (IOCs)
- Mitigation strategies
- Blue team recommendations

---

## ⚖️ Legal & Ethical Notice

### Authorized Testing Only
- Obtain written permission
- Define clear scope
- Follow rules of engagement
- Report findings responsibly

### Consequences of Unauthorized Use
- Federal criminal charges
- Prison sentences (up to 10 years)
- Substantial fines
- Civil liability
- Career impact

---

## 🚀 Getting Started

1. Read `00-MASTER-GUIDE.md` for overview
2. Begin with Module 1: Antivirus Fundamentals
3. Follow lab exercises in each module
4. Test against Windows Defender
5. Adapt techniques for your scenarios
6. Document all results and IOCs

---

## 📝 Version Info

**Version:** 1.0
**Release Date:** 2026-09-30
**Status:** Complete Documentation
**Content:** 2,000+ lines with 100+ code examples
**Techniques:** 50+ detailed methods

---

## ✨ Features

- ✅ Completely generic format
- ✅ No personal names or attribution
- ✅ Lab-ready instructions
- ✅ Step-by-step guides
- ✅ Complete code examples
- ✅ Practical exercises
- ✅ Detection countermeasures
- ✅ Real-world scenarios

---

**For Authorized Testing & Educational Purposes Only**
**Last Updated: 2026-09-30**
