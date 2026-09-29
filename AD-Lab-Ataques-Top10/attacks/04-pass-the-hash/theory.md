# Pass-the-Hash

# Teoria

O Pass-the-Hash (PtH) é um dos ataques mais clássicos e fundamentais de movimentação lateral. A sua grande sacada é que o atacante não precisa saber a senha em texto claro do usuário para invadir um sistema; o valor "embaralhado" (o hash) é o suficiente.

Aqui está a explicação teórica de como ele funciona:

O Conceito: Como o Windows trata senhas
Quando você digita sua senha no Windows, ele não a armazena como "Senha123". Ele a transforma em um código matemático chamado Hash NTLM.

No protocolo de autenticação NTLM (muito usado em redes Windows), o servidor não pede sua senha. Ele envia um "desafio" (um número aleatório) e pede que você o criptografe usando o seu hash. Se o resultado bater com o que o servidor tem guardado, você está autenticado.

O segredo do ataque: Para o sistema, o hash é a credencial. Se você tem o hash, você é o usuário.

O Mecanismo do Ataque
O Cenário de Vulnerabilidade
O ataque ocorre quando um atacante consegue privilégios de administrador local em uma máquina da rede (geralmente uma estação de trabalho).

No Windows, as credenciais de usuários que fizeram login recentemente ficam armazenadas na memória do processo LSASS (Local Security Authority Subsystem Service).

O Fluxo do Ataque
Extração (Dumping): O atacante usa ferramentas como Mimikatz ou Impacket para ler a memória do processo LSASS e extrair os hashes NTLM dos usuários logados.

A Identidade Roubada: Imagine que um Administrador de TI logou naquela máquina para dar suporte e foi embora. O hash dele ainda pode estar na memória. O atacante captura esse hash (ex: aad3b435b51404eeaad3b435b51404ee).

A Passagem (Pass): Em vez de tentar "quebrar" o hash para descobrir a senha real, o atacante simplesmente injeta esse hash em sua própria sessão de rede ou o utiliza em ferramentas de conexão remota.

Acesso Remoto: O atacante se conecta a outro computador (ex: o Controlador de Domínio ou um Servidor de Arquivos) enviando o hash roubado. O servidor aceita o hash como prova de identidade e concede acesso total.