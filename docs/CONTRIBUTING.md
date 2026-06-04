# Contribuindo com o ConciliaIA

Obrigado por contribuir! Este guia cobre o fluxo prático de desenvolvimento.

## Ambiente

Backend (Python 3.11):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # ajuste DATABASE_URL e SECRET_KEY
alembic upgrade head
uvicorn src.api.main:app --reload --port 8000
```

Frontend:

```bash
cd conciliaai-frontend && npm install && npm run dev
```

Ver também [`../README.md`](../README.md) e
[`CONFIGURATION-GUIDE.md`](CONFIGURATION-GUIDE.md).

## Fluxo de contribuição

1. Crie um branch a partir de `master`:
   `git checkout -b feat/minha-mudanca` (ou `fix/...`, `docs/...`, `chore/...`).
2. Faça mudanças pequenas e coesas, com testes.
3. Rode lint e testes localmente (abaixo).
4. Commits claros e descritivos (recomendado: Conventional Commits —
   `feat:`, `fix:`, `docs:`, `chore:`, `test:`).
5. Abra um PR para `master` descrevendo o quê e o porquê. O CI precisa ficar verde.

## Lint e testes

```bash
flake8 src/ tests/                          # estilo (config em setup.cfg)
mypy src/                                   # tipos (advisory; não bloqueia o CI)
pytest tests/unit                           # unitários
pytest tests/integration -m integration     # integração (requer Postgres)
```

Frontend:

```bash
cd conciliaai-frontend
npm run lint
npm run type-check
npm run test:unit
```

O CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) roda
flake8 → mypy (advisory) → `alembic upgrade head` → `pytest tests/unit` →
`pytest tests/integration` em `master`/`main`/`develop`.

## Estilo e convenções

- **Python:** type hints; siga o padrão do código vizinho; `flake8` deve passar
  (linha até 120 colunas, ver `setup.cfg`). Evite imports não usados.
- **Arquitetura:** respeite as fronteiras de módulo — a app é
  `src/{api,application,domain,infrastructure}`. Regras de negócio ficam no
  domínio/aplicação, não nas rotas.
- **Banco:** mudanças de schema vão por **migration Alembic** (nunca edite o banco
  à mão). Gere com `alembic revision -m "..."` e teste `upgrade`/`downgrade`.
- **API:** mantenha a versão (`/api/v1`), o envelope de erro
  `{detail, error_code, request_id}` e contratos estáveis.
- **Testes:** toda correção de bug deve vir com um teste que falha antes do fix.

## Documentação

Mudanças de comportamento/contrato devem atualizar a doc correspondente em
`docs/` (ex.: [`API-REFERENCE.md`](API-REFERENCE.md),
[`SECURITY.md`](SECURITY.md), [`ARCHITECTURE-POSTURE.md`](ARCHITECTURE-POSTURE.md)).

## Código de conduta

Ao participar, você concorda com o [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
