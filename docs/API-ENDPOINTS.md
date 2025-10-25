# API Endpoints

## Import Transactions from EDI

**Endpoint:** `POST /api/v1/transactions/import-edi`

**Description:** Import transactions directly from acquirer EDI files (text format).

**Authentication:** Required (Bearer token)

**Query Parameters:**
- `acquirer` (string, default: "rede"): Acquirer name
  - Supported: `rede`, `cielo` (coming soon), `stone` (coming soon)

**Request Body:**
- `file` (file): EDI file in text format (.txt, .edi)

**Supported Formats:**
- **Rede:** EEVC (Extrato Eletrônico de Vendas Crédito) v3.00

**Response:**
```json
{
  "imported": 18,
  "failed": 0,
  "errors": []
}
```

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/transactions/import-edi?acquirer=rede" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@rede_eevc_test.txt"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/transactions/import-edi"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"file": open("rede_eevc_test.txt", "rb")}
params = {"acquirer": "rede"}

response = requests.post(url, headers=headers, files=files, params=params)
print(response.json())
```

**Error Codes:**
- `400`: Invalid file format or unsupported acquirer
- `401`: Unauthorized (missing or invalid token)
- `500`: Internal server error
