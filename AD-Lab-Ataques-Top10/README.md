# 🔴 Laboratório de Ataques em Active Directory (Top 10)

Uma simulação completa de **10 técnicas críticas** usadas em operações Red Team e testes de penetração em ambientes Active Directory.

Cada ataque é documentado com:
- 📖 **Teoria** — Explicação da técnica e contexto técnico
- 🏗️ **Lab Setup** — Configuração passo-a-passo do ambiente
- ⚔️ **Exploitation** — Comandos reais e POCs funcionais
- 🔍 **Detection** — Indicadores e logs para detectar o ataque
- 🛡️ **Mitigation** — Estratégias de defesa e hardening

---

## 🎯 Técnicas Cobertas

| # | Técnica | MITRE ATT&CK | Tática |
|---|---------|--------------|--------|
| 01 | Kerberoasting | T1558.003 | Credential Access |
| 02 | ASREPRoasting | T1558.004 | Credential Access |
| 03 | DCSync | T1003.006 | OS Credential Dumping |
| 04 | Pass-the-Hash | T1550.002 | Use Alternate Auth Material |
| 05 | Pass-the-Ticket | T1550.003 | Use Alternate Auth Material |
| 06 | Golden Ticket | T1556.001 | Modify Authentication Process |
| 07 | Silver Ticket | T1556.001 | Modify Authentication Process |
| 08 | ADCS Abuse | T1187 | Forced Authentication |
| 09 | GPO Abuse | T1484.001 | Domain Policy Modification |
| 10 | Unconstrained Delegation | T1187 | Forced Authentication |

---

## 🏛️ Topologia do Laboratório

```
                     ┌─────────────────┐
                     │  Kali Linux     │
                     │   (Atacante)    │
                     └────────┬────────┘
                              │
                    ┌─────────┼─────────┐
                    │                   │
          ┌─────────▼────────┐  ┌──────▼──────────┐
          │  Windows Server  │  │  Windows 10     │
          │  (Domain DC)     │  │  (Workstation1) │
          │  lab.local       │  │  Member         │
          └────────┬─────────┘  └──────┬──────────┘
                   │                   │
          ┌────────▼──────────────────┘
          │
    ┌─────▼──────────┐
    │  Windows 10    │
    │  (Workstation2)│
    │  Member        │
    └────────────────┘

Network: 192.168.56.0/24
Domain: lab.local
```

---

## 📋 Requisitos

**Hardware Recomendado:**
- 16GB RAM mínimo
- 50GB espaço livre
- Hypervisor: VirtualBox, Hyper-V ou VMware

**Software:**
- Kali Linux 2024+
- Windows Server 2019+
- Windows 10 Pro+
- Ferramentas: BloodHound, Impacket, CrackMapExec, Mimikatz, Rubeus

---

## 🚀 Quick Start

```bash
# Clone o repositório
git clone https://github.com/Vitor-Oliveira84/AD-Lab-Ataques-Top10.git
cd AD-Lab-Ataques-Top10

# Veja a documentação de cada ataque
ls attacks/
cd attacks/01-kerberoasting/
cat theory.md          # Entenda a técnica
cat lab-setup.md       # Configure o lab
cat exploitation.md    # Execute o ataque
cat detection.md       # Detecte o ataque
cat mitigation.md      # Mitigue a vulnerabilidade
```

---

## 📚 Estrutura

```
AD-Lab-Ataques-Top10/
├── attacks/
│   ├── 01-kerberoasting/
│   │   ├── theory.md
│   │   ├── lab-setup.md
│   │   ├── exploitation.md
│   │   ├── detection.md
│   │   └── mitigation.md
│   ├── 02-asrep-roasting/
│   ├── 03-dcsync/
│   ├── 04-pass-the-hash/
│   ├── 05-pass-the-ticket/
│   ├── 06-golden-ticket/
│   ├── 07-silver-ticket/
│   ├── 08-adcs-abuse/
│   ├── 09-gpo-abuse/
│   └── 10-unconstrained-delegation/
├── architecture/
│   └── lab-topology.png
└── README.md
```

---

## 🎓 Público Alvo

✅ Profissionais de segurança em transição para Red Team
✅ Pentesters que querem dominar ataques em AD
✅ Defensores que precisam entender técnicas adversárias
✅ Estudantes de segurança ofensiva

---

## 🔗 Referências

- [MITRE ATT&CK Framework](https://attack.mitre.org)
- [Bloodhound Documentation](https://bloodhound.readthedocs.io)
- [Impacket](https://github.com/fortra/impacket)
- [Rubeus](https://github.com/GhostPack/Rubeus)

---

## ⚖️ Licença

Apenas para fins educacionais e testes autorizados em ambientes próprios.