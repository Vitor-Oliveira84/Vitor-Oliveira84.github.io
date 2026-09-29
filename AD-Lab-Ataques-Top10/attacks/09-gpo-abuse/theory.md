# Abuso de GPO

# Teoria

Como a Exploração Funciona
O ataque não explora um "bug" no código do Windows, mas sim permissões mal configuradas.

O Cenário de Vulnerabilidade
Para que o abuso ocorra, um usuário comum (ou um grupo ao qual ele pertence) deve ter permissões de Escrita (Write) ou Modificação (Edit) em um objeto de GPO. Isso acontece frequentemente por:

Erros de delegação de privilégios.

Contas de suporte técnico com permissões excessivas.

GPOs antigas "esquecidas" com permissões abertas.

O Vetor de Ataque
Assim que o atacante compromete uma conta com permissão de escrita na GPO, o fluxo é o seguinte:

Identificação: O atacante usa ferramentas (como PowerView ou BloodHound) para encontrar GPOs que ele pode modificar.

Injeção de Código: O atacante altera a GPO para realizar uma ação maliciosa. Exemplos comuns:

Adicionar um novo Administrador: Criar um usuário ou adicionar um usuário existente ao grupo "Administradores Locais".

Agendar uma Tarefa (Scheduled Task): Comandar todas as máquinas para baixar e executar um malware (como um Ransomware ou um Reverse Shell).

Mudar permissões de registro: Para desativar o antivírus.

Aguardar a Replicação: O atacante não precisa fazer mais nada. Ele apenas espera o ciclo de atualização do Windows.

Execução: Os computadores do domínio baixam a diretiva alterada e executam o comando do atacante com privilégios de SYSTEM (o nível mais alto de acesso local).