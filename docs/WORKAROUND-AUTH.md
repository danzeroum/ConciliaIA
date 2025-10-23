# 🔧 Workaround - Autenticação Temporária

## ⚠️ ATENÇÃO
Este é um workaround temporário para o MVP. 
**NÃO USAR EM PRODUÇÃO!**

## Credenciais de Teste

- **Email:** test@example.com
- **Senha:** SecurePassword123!

## Como Funciona

1. Backend valida credenciais contra usuário hardcoded
2. Retorna JWT válido se credenciais corretas
3. Retorna 401 se credenciais inválidas

## TODO - Próximos Passos

- [ ] Implementar tabela `users` no PostgreSQL
- [ ] Criar migration para usuários
- [ ] Implementar UserRepository
- [ ] Substituir lógica hardcoded por busca real no banco
- [ ] Adicionar registro de usuários
- [ ] Implementar recuperação de senha

## Remover Workaround

Quando implementar autenticação real, remover:
- Constante `TEST_USER` em `src/api/routes/auth.py`
- Este arquivo de documentação
