# Kerberoasting

# Teoria

O Kerberoasting é um dos ataques mais populares e eficazes em ambientes Active Directory. Diferente do AS-REP Roasting (que foca em contas de usuários comuns com configurações raras), o Kerberoasting foca em contas de serviço.

O grande trunfo deste ataque é que ele não exige vulnerabilidades de software ou configurações erradas exóticas; ele explora o design fundamental do protocolo Kerberos

O Conceito: Service Principal Names (SPN)
No Active Directory, quando um serviço (como um Banco de Dados SQL, um Servidor de E-mail ou um IIS) precisa rodar no contexto de uma conta de usuário, ele usa um SPN.

O SPN vincula um serviço (ex: MSSQLSvc/sql01.corp.local) a uma conta de usuário específica no AD.

Para que um usuário possa acessar esse serviço, o Kerberos precisa fornecer um Ticket de Serviço (TGS).

O Mecanismo do Ataque
O ataque baseia-se em um fato crucial do Kerberos: Qualquer usuário autenticado no domínio pode solicitar um ticket de serviço para qualquer SPN registrado.

O Fluxo do Ataque
Enumeração de SPNs: O atacante, usando uma conta de usuário comum (sem privilégios), faz uma consulta ao Active Directory perguntando: "Quais contas de usuário têm um SPN associado?". O AD responde com uma lista de contas de serviço.

Solicitação de Ticket (TGS-REQ): O atacante solicita ao Controlador de Domínio (DC) um ticket para acessar um desses serviços (ex: o SQL Server).

Entrega do Ticket (TGS-REP): O DC gera um ticket de serviço. Este ticket contém uma parte dos dados que é criptografada usando o hash da senha da conta de serviço. O DC envia esse ticket para o usuário (o atacante).

Extração da Memória: O atacante não tenta "usar" o ticket para acessar o serviço real. Em vez disso, ele extrai o ticket da memória do seu próprio computador.

Quebra Offline (Cracking): O atacante leva o ticket para sua máquina de ataque (Kali Linux). Como o ticket foi criptografado com a senha do serviço, o atacante tenta "adivinhar" essa senha usando força bruta ou dicionários (Wordlists). Se ele encontrar a senha correta, ele consegue descriptografar o ticket.