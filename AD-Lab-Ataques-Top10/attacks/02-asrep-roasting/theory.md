# AS-REP Roasting

# Teoria

O AS-REP Roasting é um ataque de extração de credenciais que foca em uma configuração específica (e insegura) de contas de usuário no Active Directory.

Diferente do Kerberoasting (que foca em contas de serviço), o AS-REP Roasting foca em contas de usuários comuns que possuem uma propriedade habilitada chamada: "Do not require Kerberos preauthentication" (Não exigir pré-autenticação Kerberos).

O que é a Pré-Autenticação Kerberos?
Para entender o ataque, precisamos entender a defesa que ele pula:

Fluxo Normal: Quando você tenta logar, seu computador envia uma solicitação (AS-REQ) ao Controlador de Domínio (DC). Essa solicitação contém um carimbo de data/hora (timestamp) criptografado com o hash da sua senha. O DC descriptografa isso para provar que você sabe a senha antes de te enviar qualquer coisa.

Sem Pré-Autenticação: Se essa opção estiver marcada na conta do usuário, o DC não pede prova de identidade. Ele simplesmente assume que quem pediu é quem diz ser e envia de volta uma resposta (AS-REP).

O Mecanismo do Ataque
O ataque explora o fato de que a resposta do servidor (AS-REP) contém uma parte dos dados que é criptografada com a senha do usuário.

O Fluxo do Ataque
Enumeração: O atacante usa ferramentas (como o GetADUsers.py do Impacket) para listar todos os usuários do domínio que têm a configuração "Do not require Kerberos preauthentication" ativa. Qualquer usuário da rede pode fazer essa consulta ao AD.

A Solicitação: O atacante envia uma mensagem de solicitação de autenticação (AS-REQ) para o DC em nome desses usuários vulneráveis. Como a pré-autenticação está desativada, o DC não pede senha.

A Resposta: O DC responde com um pacote AS-REP. Dentro desse pacote, há uma chave de sessão criptografada com o hash da senha do usuário.

Quebra Offline: O atacante captura esse pacote, leva para sua máquina (Kali Linux) e tenta "adivinhar" a senha usando ferramentas de força bruta como o Hashcat ou John the Ripper. Se ele acertar a senha, ele conseguirá descriptografar o pacote