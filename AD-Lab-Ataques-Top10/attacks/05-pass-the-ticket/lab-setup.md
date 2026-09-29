
# Configuração do Laboratório

Exemplo:

Criar conta vulnerável:

```
New-ADUser svc_sql -AccountPassword (ConvertTo-SecureString "Password123!" -AsPlainText -Force) -Enabled $true
setspn -a MSSQLSvc/sql.lab.local svc_sql
```
