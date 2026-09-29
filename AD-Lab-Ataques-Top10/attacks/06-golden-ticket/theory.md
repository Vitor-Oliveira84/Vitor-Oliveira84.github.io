# Golden Ticket

# Teoria

O Golden Ticket é o "chefe final" dos ataques de Active Directory. Se o Pass-the-Ticket é roubar um ingresso de alguém, o Golden Ticket é como roubar a máquina que imprime os ingressos.

Com ele, o atacante detém o controle total, persistente e virtualmente indetectável de todo o domínio.

O Golden Ticket é o "chefe final" dos ataques de Active Directory. Se o Pass-the-Ticket é roubar um ingresso de alguém, o Golden Ticket é como roubar a máquina que imprime os ingressos.

Com ele, o atacante detém o controle total, persistente e virtualmente indetectável de todo o domínio.

1. O Conceito: A conta KRBTGT
No coração do Kerberos existe uma conta especial chamada krbtgt. Ela é criada automaticamente quando o domínio é instalado e possui uma função única:

A senha dessa conta é usada para criptografar e assinar todos os TGTs (os crachás de entrada) do domínio.

Se você possui o hash da senha da conta krbtgt, você pode forjar seu próprio TGT.

O Mecanismo do Ataque
O Golden Ticket não é um "roubo" de um ticket existente; é a criação manual de um ticket falso que o Active Directory será obrigado a aceitar como legítimo.

O Fluxo da Exploração
Dominação Inicial: O atacante precisa primeiro comprometer um Controlador de Domínio (DC) ou usar o ataque DCSync para obter o hash NTLM da conta krbtgt.

Forjando o Ticket: De posse do hash da krbtgt, o atacante usa ferramentas (como o Mimikatz ou Rubeus) para gerar um arquivo de ticket (.kirbi). Na criação, ele pode definir:

Qualquer Nome de Usuário: Pode ser um usuário que nem existe.

Qualquer Grupo: Ele se coloca no grupo "Domain Admins".

Validade Extrema: O padrão do Kerberos é 10 horas, mas um Golden Ticket pode ser configurado para durar 10 anos ou mais.

Injeção e Uso: O atacante injeta esse ticket na memória de qualquer máquina da rede. Quando ele tenta acessar um recurso, o DC olha a assinatura do ticket, vê que foi "assinado" pela chave da krbtgt e concede acesso total, sem questionar.