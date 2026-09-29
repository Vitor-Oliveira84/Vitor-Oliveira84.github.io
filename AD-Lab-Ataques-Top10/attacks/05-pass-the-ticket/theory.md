# Pass-the-Ticket

# Teoria

O Pass-the-Ticket (PtT) é o "irmão" do Pass-the-Hash, mas focado no protocolo Kerberos em vez do NTLM. Enquanto no PtH você rouba o hash da senha, no PtT você rouba os Tickets (ingressos) que o Windows armazena na memória.

A grande vantagem para o atacante aqui é que, ao usar tickets, ele pode evitar sistemas que monitoram especificamente o uso de hashes NTLM e se misturar ao tráfego legítimo do Kerberos.

O Conceito: A Memória do Windows
Quando você faz login em um domínio, o Windows solicita um TGT (Ticket Granting Ticket) ao Controlador de Domínio. Esse TGT fica guardado na memória (no processo LSASS) para que, sempre que você precisar acessar uma pasta compartilhada ou um e-mail, o Windows o use automaticamente sem te pedir a senha de novo.

O ataque consiste em extrair esse ticket da memória de um usuário e injetá-lo na sessão do atacante.

O Mecanismo do Ataque
O Fluxo da Exploração
Acesso Inicial: O atacante precisa de privilégios de administrador local em uma máquina onde um usuário alvo (ex: um Administrador de Rede) está logado ou esteve logado recentemente.

Exportação do Ticket: Usando ferramentas como o Mimikatz (comando sekurlsa::tickets /export), o atacante extrai todos os tickets Kerberos que estão na memória RAM. Esses tickets são salvos como arquivos com a extensão .kirbi.

A Injeção (O "Pulo"): O atacante pega o arquivo .kirbi roubado e o "injeta" em seu próprio processo na memória (comando kerberos::ptt).

Acesso Direto: Agora, quando o atacante tenta acessar um recurso na rede (como o C$ de um servidor), o Windows não olha para a senha do atacante; ele olha para o ticket injetado na memória. O servidor de destino aceita o ticket e concede o acesso.

Os Tipos de Tickets Roubados
Existem dois tipos principais que podem ser "passados":

TGT (Ticket Granting Ticket): É o mais valioso. Se o atacante rouba o TGT de um administrador, ele pode pedir tickets para qualquer serviço na rede em nome desse administrador.

TGS (Service Ticket): É um ticket para um serviço específico (ex: apenas para o servidor de arquivos). É mais limitado, mas ainda útil se o alvo for o servidor onde estão os dados sensíveis.