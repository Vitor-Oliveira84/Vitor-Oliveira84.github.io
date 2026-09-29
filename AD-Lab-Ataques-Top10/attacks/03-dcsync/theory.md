# DCSync

# Teoria

O Gemini disse
O ataque DCSync é considerado um dos "santos graais" do pós-exploração em Active Directory. Diferente de outros ataques que tentam quebrar senhas ou explorar bugs, o DCSync simula o comportamento legítimo de um Controlador de Domínio (DC).

O Conceito: Replicação de Diretório
Em uma rede grande, existem vários Controladores de Domínio (DCs). Para que todos tenham as mesmas informações (usuários, senhas, grupos), eles precisam "conversar" e sincronizar seus bancos de dados constantemente.

Essa sincronização utiliza um protocolo chamado MS-DRSR (Directory Replication Service Remote Protocol). Quando um DC quer atualizar seus dados, ele pede ao outro: "Ei, sou um DC parceiro, por favor, envie-me as atualizações do banco de dados de usuários".

O Mecanismo do Ataque
O DCSync não precisa de acesso direto ao arquivo físico do banco de dados do AD (o ntds.dit). Em vez disso, o atacante utiliza as APIs do protocolo de replicação para solicitar os dados.

O Cenário de Vulnerabilidade
O ataque baseia-se puramente em permissões de escrita/leitura no objeto do Domínio. Para que uma conta consiga realizar um DCSync, ela precisa de duas permissões específicas no nível do domínio:

DS-Replication-Get-Changes

DS-Replication-Get-Changes-All

Por padrão, apenas os grupos Administradores do Domínio, Administradores de Empresa e Controladores de Domínio possuem essas permissões.

O Fluxo do Ataque
Comprometimento: O atacante obtém o controle de uma conta que possua as permissões acima (ou escala privilégios até se tornar Admin do Domínio).

A Solicitação: Utilizando uma ferramenta como o Mimikatz ou secretsdump.py, o atacante envia uma solicitação de replicação para um DC real.

A Resposta: O DC alvo verifica as permissões. Como a conta do atacante "tem o direito" de replicar, o DC acredita que está falando com outro servidor legítimo e envia os hashes de senha solicitados (incluindo o hash da conta krbtgt e de todos os administradores).