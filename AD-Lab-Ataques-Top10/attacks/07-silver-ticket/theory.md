# Silver Ticket

# Teoria

O Golden Ticket é o ataque de persistência mais poderoso em um ambiente Active Directory. Se o Pass-the-Ticket consiste em roubar um ingresso de alguém, o Golden Ticket é como roubar a máquina que imprime os ingressos.

Com ele, o atacante detém o controle total, vitalício e virtualmente indetectável de todo o domínio.

O Conceito: A conta KRBTGT
No coração do protocolo Kerberos existe uma conta especial chamada krbtgt. Ela é o "segredo mestre" do domínio:

A senha (ou o hash NTLM) desta conta é usada para criptografar e assinar todos os TGTs (os tickets de entrada) emitidos pelo Controlador de Domínio.

Como o sistema confia cegamente em qualquer ticket assinado pela chave krbtgt, se você possui esse hash, você pode forjar seu próprio "crachá de entrada".

O Mecanismo do Ataque
O Golden Ticket não é o roubo de um ticket existente; é a criação manual de um ticket falso que o Active Directory será obrigado a aceitar como legítimo.

O Fluxo da Exploração
Dominação Inicial: O atacante precisa primeiro obter o hash NTLM da conta krbtgt. Isso geralmente é feito através do ataque DCSync ou acessando diretamente o banco de dados ntds.dit de um Controlador de Domínio comprometido.

Forjando o Ticket: De posse do hash da krbtgt, do nome do domínio e do SID (Security Identifier) do domínio, o atacante usa ferramentas como o Mimikatz ou Rubeus para gerar o ticket. Na criação, ele pode definir:

Qualquer Nome de Usuário: Pode ser um usuário real ou um nome fictício.

Privilégios Totais: Ele se insere manualmente no grupo "Domain Admins" (RID 512).

Validade Extrema: O padrão do Kerberos é 10 horas, mas um Golden Ticket pode ser configurado para durar 10 anos ou mais.

Injeção e Uso: O atacante injeta esse ticket forjado na memória de sua máquina. Quando ele tenta acessar qualquer servidor, o alvo envia o ticket ao DC para validação. O DC vê que o ticket foi "assinado" pela chave da krbtgt e concede acesso total imediatamente.
