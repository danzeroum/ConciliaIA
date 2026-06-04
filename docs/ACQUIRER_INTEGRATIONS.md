# Integrações com Adquirentes

O ConciliaIA importa relatórios de adquirentes através de **parsers plugáveis**.
O ponto único de verdade é o registro em
[`src/infrastructure/acquirers/registry.py`](../src/infrastructure/acquirers/registry.py),
exposto pela API em **`GET /api/v1/acquirers`** — o frontend não depende de um
enum hardcoded.

## Endpoint

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/acquirers
```

Retorna, para cada adquirente: `id`, `label`, `parser_formats` (formatos com
parser registrado) e `supported` (se há pelo menos um parser).

## Adquirentes e formatos suportados

| Adquirente | `id` | Formatos com parser | Suportado |
|---|---|---|---|
| Cielo | `cielo` | `agiliza`, `edi` | ✅ |
| Rede | `rede` | `edi`, `eefi`, `torc` | ✅ |
| Stone | `stone` | `api` | ✅ |
| Mercado Pago | `mercadopago` | — | ❌ (sem parser ainda) |
| GetNet | `getnet` | — | ❌ (sem parser ainda) |
| PagSeguro | `pagseguro` | — | ❌ (sem parser ainda) |

Parsers (em `src/infrastructure/acquirers/`):

- **Cielo:** `CieloAgilizaParser` (CSV do portal Agiliza), `CieloEDIParser` (EDI).
- **Rede:** `RedeEDIParser` (EEVC/EEVD/EEFI posicional), `RedeEEFIParser`,
  `RedeTORCParser` (usado por `POST /api/v1/ingestion/rede-torc`).
- **Stone:** `StoneParser` (payload da API).

Todos herdam de `BaseAcquirerParser` (Template Method): `parse(raw, tenant_id)`
→ `List[AcquirerTransaction]`, normalizando para o modelo canônico do domínio.

## Como adicionar um novo adquirente/formato

1. Implemente uma subclasse de `BaseAcquirerParser`.
2. Registre-a em `ACQUIRER_PARSERS` no `registry.py` sob o `Acquirer` e o
   `format_id` correspondentes.

Com isso, `GET /api/v1/acquirers` e a UI passam a refletir o novo formato sem
edições espalhadas.

## Importação

- Transações via EDI: `POST /api/v1/transactions/import-edi?acquirer=<id>`.
- Cielo Conciliator (integração HTTP): `POST /api/v1/cielo-conciliator/import`
  (requer `CIELO_CONCILIATOR_*`; a app sobe sem elas e a rota retorna 503 até a
  configuração).
- Rede TORC: `POST /api/v1/ingestion/rede-torc`.
