# ConciliaIA — Segurança

Este documento descreve os controles de segurança **efetivamente implementados**
no código. Itens planejados/futuros estão marcados como tal.

## Autenticação

- **JWT (HS256)** — assinado com `SECRET_KEY` (obrigatória; a app não sobe sem ela).
  `JWTHandler` em `src/infrastructure/security/jwt_handler.py`.
- **Login:** `POST /api/v1/auth/login` com `{email, password}` (e-mail validado por
  `EmailStr`) retorna `{access_token, refresh_token, token_type:"bearer", expires_in}`.
- **Access token** de curta duração (≈15 min; `expires_in=900`) + **refresh token**.
- **Senhas:** hash **bcrypt com 12 rounds** (`PasswordHasher(rounds=12)`,
  `src/infrastructure/security/password_hasher.py`). Senhas nunca são armazenadas em claro.

## Autorização e isolamento por tenant

- `JWTContextMiddleware` decodifica o token uma única vez e popula
  `request.state` (`tenant_id`, `user_id`, `email`, `roles`) **antes** dos demais
  middlewares. Requisições à superfície protegida (`/api/v1/*`, exceto
  `/api/v1/health` e `/api/v1/auth/*`) **sem token válido recebem 401**.
- `TenantMiddleware` garante que toda requisição protegida esteja escopada a um
  tenant; tentativas de acessar outro tenant via path/query retornam **403**.
- **RBAC:** dependência `require_roles(...)` (`src/api/dependencies.py`) protege
  endpoints por papel; os papéis vêm do JWT (`roles`).

## Rate limiting

- `RateLimitMiddleware` (token bucket por tenant/IP). Default **100 req/min**
  (`RATE_LIMIT_REQUESTS_PER_MINUTE` / `RATE_LIMIT_PER_MINUTE`). Excedido → **429**
  com `Retry-After`. Estático/SPA e healthcheck ficam fora do limite.

## Cabeçalhos de segurança

Emitidos para toda resposta (`src/api/main.py`):

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains`
- `Server: ConciliaAI`

> Nota: **não** são emitidos hoje `Content-Security-Policy`, `Referrer-Policy`
> nem `X-XSS-Protection`. Adicioná-los é melhoria recomendada.

## CORS

Origens explícitas (não wildcard, pois `allow_credentials=True`). Em
desenvolvimento: `localhost:3000`/`5173`. Em produção, definidas via
`CORS_ORIGINS`. Na imagem única (mesma origem), CORS é irrelevante para o app.

## Observabilidade / correlação

- Toda resposta carrega `X-Request-ID`.
- Erros seguem o envelope `{ detail, error_code, request_id }`
  (`src/api/errors.py`) — base para correlação em logs estruturados (structlog).

## Precisão financeira

- Valores monetários: colunas `Numeric(15,2)` no banco e `Money`/`Decimal` no
  domínio. Na fronteira da API são tipados como `Decimal` e serializados como
  número JSON (`src/api/serialization.py`), sem perda na lógica de negócio.

## Segredos e configuração

- `SECRET_KEY` deve ser gerada por ambiente (`openssl rand -hex 32`) e **nunca**
  versionada. O `docker-compose.yml` traz um default APENAS para desenvolvimento;
  **defina `SECRET_KEY` em produção**.
- Credenciais da Cielo Conciliator são opcionais no boot (a app sobe sem elas; as
  rotas Cielo retornam 503 até serem configuradas).

## Não implementado (backlog)

Os controles abaixo **não** existem no código atual e são candidatos a roadmap:

- **Account lockout / bloqueio por tentativas** de login.
- **Row-Level Security (RLS)** no PostgreSQL — o isolamento hoje é feito na
  camada de aplicação (middleware + filtros por `tenant_id` nas queries), não por
  policies do banco.
- `Content-Security-Policy` / `Referrer-Policy`.
- Rotação automática de segredos / KMS.

## Reporte de vulnerabilidades

Reporte de forma responsável (não abra issue pública com detalhes exploráveis).
Use o canal de segurança do repositório.
