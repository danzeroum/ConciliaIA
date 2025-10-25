#!/bin/bash
# Test Rede EDI upload manually

set -e

API_URL="${API_URL:-http://localhost:8000}"
EDI_FILE="${1:-demo_data/rede_oficial/rede_eevc_test.txt}"

echo "🧪 Testing Rede EDI Upload"
echo "=========================="
echo "API URL: $API_URL"
echo "EDI File: $EDI_FILE"
echo ""

# Check if file exists
if [ ! -f "$EDI_FILE" ]; then
    echo "❌ Error: EDI file not found: $EDI_FILE"
    exit 1
fi

echo "📄 EDI File Info:"
wc -l "$EDI_FILE"
echo ""

# Login to get token
echo "🔐 Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }')

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Error: Failed to get access token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Upload EDI
echo "📤 Uploading EDI file..."
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/transactions/import-edi?acquirer=rede" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$EDI_FILE")

echo "$UPLOAD_RESPONSE" | jq .

# Check result
IMPORTED=$(echo "$UPLOAD_RESPONSE" | jq -r '.imported')
FAILED=$(echo "$UPLOAD_RESPONSE" | jq -r '.failed')

echo ""
echo "📊 Upload Summary:"
echo "   Imported: $IMPORTED"
echo "   Failed: $FAILED"

if [ "$IMPORTED" -gt 0 ]; then
    echo ""
    echo "✅ Success! Imported $IMPORTED transactions"
    
    # List transactions
    echo ""
    echo "📋 Listing recent transactions..."
    curl -s -X GET "$API_URL/api/v1/transactions?acquirer=rede&page_size=5" \
        -H "Authorization: Bearer $TOKEN" | jq '.items[] | {nsu: .nsu, amount: .amount, date: .transaction_date}'
    
    exit 0
else
    echo ""
    echo "⚠️  No transactions imported"
    
    if [ "$FAILED" -gt 0 ]; then
        echo "❌ Failed to import $FAILED transactions"
        echo "$UPLOAD_RESPONSE" | jq '.errors'
    fi
    
    exit 1
fi
