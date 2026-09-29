# Abuso de ADCS

# Teoria

O ataque de Abuso do ADCS (Active Directory Certificate Services) é um dos vetores de escalonamento de privilégios mais críticos descobertos nos últimos anos. Ele foca na infraestrutura de PKI (Public Key Infrastructure) da Microsoft.

Em termos simples: o ADCS é o cartório do domínio. Ele emite certificados digitais para usuários e computadores provarem quem são. Se você enganar o "cartório", ele te dá um certificado de Administrador do Domínio.

O que é o ADCS?
O ADCS é uma função de servidor que permite criar uma Autoridade Certificadora (CA). As empresas o usam para:

Criptografia de e-mails (S/MIME).

Autenticação em VPNs ou Wi-Fi.

Smart Card Logon (Autenticação baseada em certificado).

O problema surge nos Templates de Certificado (modelos), que definem as regras para quem pode pedir um certificado e o que esse certificado pode fazer.

Como a Exploração Funciona (A Teoria)
A pesquisa fundamental sobre isso (chamada Certified Pre-Owned) identificou várias vulnerabilidades conceituais, geralmente rotuladas como ESC1 até ESC13.

Aqui está o funcionamento do cenário mais comum (ESC1):

O Cenário de Vulnerabilidade
Para o ataque funcionar, um Template de Certificado precisa ter três falhas simultâneas:

Permissões excessivas: Usuários comuns (Domain Users) têm permissão para solicitar o certificado.

Uso de Autenticação: O certificado permite "Client Authentication" (pode ser usado para fazer login).

SAN (Subject Alternative Name) Editável: Esta é a falha crítica. O template permite que o solicitante diga quem ele é no campo SAN.

O Fluxo do Ataque
Identificação: O atacante usa ferramentas como Certify ou BloodHound para encontrar templates vulneráveis.

Solicitação Falsa: O atacante (como um usuário comum, ex: joao) solicita um certificado baseado no template vulnerável.

Personificação: Na solicitação, ele preenche o campo SAN como administrator@empresa.com.

Emissão: O ADCS olha o template, vê que o joao tem permissão para pedir e que o template permite definir o SAN. O servidor emite um certificado válido, assinado pela empresa, dizendo que o portador é o Administrador.

Login: O atacante usa esse certificado (geralmente um arquivo .pfx) para realizar um login Kerberos e obter o TGT do Administrador.

Outras Variações Comuns (ESC)

Identificador   |   Resumo do Abuso
ESC1            |   Usuário define qualquer nome no certificado (SAN).
ESC3            |   Uso de certificados de "Agente de Inscrição" para pedir certificados em nome de outros.
ESC4O           |   Atacante tem permissão de escrita no próprio Template e o torna vulnerável de propósito.
ESC8            |   HTTP NTLM Relay: O atacante intercepta a conexão de um servidor e a redireciona para a interface web do ADCS para gerar um certificado automaticamente.