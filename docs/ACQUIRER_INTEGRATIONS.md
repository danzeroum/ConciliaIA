# Acquirer Integrations

This document summarizes the ingestion strategy adopted by ConciliaAI for each supported acquirer.

## Cielo

- **Transport:** SFTP (CIELO_EC_NUMBER)
- **Format:** EDI fixed-width (Cielo layout v3)
- **Client:** `CieloEDIClient`
- **Parser:** `CieloEDIParser`
- **Schedule:** Daily D+1 downloads per establishment

## Rede

- **Transport:** SFTP (Rede gateway)
- **Format:** EDI positional files (EEVC, EEVD, EEFI, EESA)
- **Client:** `RedeEDIClient`
- **Parser:** `RedeEDIParser`
- **Highlights:**
  - Automatic detection of file type by header
  - Support for credit (parcelado), debit, financial releases and open balance files
  - Normalizes MDR rate/amount and masked PAN metadata

## Stone

- **Transport:** REST API with OAuth 2.0
- **Client:** `StoneAPIClient`
- **Parser:** `StoneParser`
- **Schedule:** Hourly polling with pagination (100 records/page)

## Validation Utilities

- `scripts/validate_rede_files.py` validates Rede EDI payloads locally
- `tests/unit/infrastructure/test_rede_edi_parser.py` provides coverage for EEVC/EEVD/EEFI records

Keep this document in sync with future integrations (e.g., GetNet, Mercado Pago) to ensure onboarding remains frictionless.
