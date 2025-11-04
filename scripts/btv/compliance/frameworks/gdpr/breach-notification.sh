#!/usr/bin/env bash
# BuildToValue v7.4-Platinum - GDPR Breach Notification (Art. 33/34)
set -euo pipefail

BREACH_LOG=".buildtovalue/compliance/breach-log.jsonl"
NOTIFICATION_TEMPLATE=".buildtovalue/compliance/templates/breach-notification.md"

###############################################################################
# Registra incidente de violação de dados
###############################################################################
register_breach() {
  local breach_type="$1"
  local description="$2"
  local affected_users="${3:-unknown}"
  local severity="${4:-high}"

  echo "🚨 Registrando violação de dados..."

  mkdir -p "$(dirname "$BREACH_LOG")"

  local breach_id="BREACH-$(date +%Y%m%d-%H%M%S)"

  local breach_entry=$(jq -n \
    --arg id "$breach_id" \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg type "$breach_type" \
    --arg desc "$description" \
    --arg users "$affected_users" \
    --arg severity "$severity" \
    '{
      breach_id: $id,
      timestamp: $ts,
      type: $type,
      description: $desc,
      affected_users: $users,
      severity: $severity,
      status: "investigating",
      notification_sent: false,
      dpa_notified: false,
      remediation_steps: []
    }'
  )

  echo "$breach_entry" >> "$BREACH_LOG"

  echo "✅ Violação registrada: $breach_id"
  echo "⚠️ ATENÇÃO: Notificação à DPA necessária em até 72 horas (Art. 33 GDPR)"

  # Verificar se notificação é obrigatória
  if [[ "$severity" == "high" ]] || [[ "$severity" == "critical" ]]; then
    echo "🔴 Severidade $severity: Notificação OBRIGATÓRIA"
  fi
}

###############################################################################
# Gera notificação de violação
###############################################################################
generate_notification() {
  local breach_id="$1"

  if [[ ! -f "$BREACH_LOG" ]]; then
    echo "❌ Log de violações não encontrado" >&2
    return 1
  fi

  local breach=$(jq -c "select(.breach_id == \"$breach_id\")" "$BREACH_LOG" | head -1)

  if [[ -z "$breach" ]]; then
    echo "❌ Violação $breach_id não encontrada" >&2
    return 1
  fi

  local output_file=".buildtovalue/compliance/reports/breach-notification-$breach_id.md"
  mkdir -p "$(dirname "$output_file")"

  cat > "$output_file" <<EOF
# Data Breach Notification
## GDPR Articles 33 & 34

---

**Breach ID:** $(echo "$breach" | jq -r '.breach_id')
**Date/Time:** $(echo "$breach" | jq -r '.timestamp')
**Status:** $(echo "$breach" | jq -r '.status')

---

## 1. Nature of the Personal Data Breach

**Type:** $(echo "$breach" | jq -r '.type')

**Description:**
$(echo "$breach" | jq -r '.description')

---

## 2. Contact Point

**Data Protection Officer:**
- Name: [DPO Name]
- Email: dpo@buildtovalue.com
- Phone: [Contact Number]

---

## 3. Likely Consequences

**Severity:** $(echo "$breach" | jq -r '.severity')

**Affected Data Subjects:** $(echo "$breach" | jq -r '.affected_users')

**Potential Impact:**
- [ ] Unauthorized access to personal data
- [ ] Data confidentiality compromised
- [ ] Data integrity affected
- [ ] Data availability disrupted

---

## 4. Measures Taken

**Immediate Actions:**
$(echo "$breach" | jq -r '.remediation_steps[] // "No remediation steps recorded yet"')

**Preventive Measures:**
- Enhanced access controls
- Additional monitoring
- Security policy review

---

## 5. Notification Status

- **Supervisory Authority (DPA):** $(echo "$breach" | jq -r 'if .dpa_notified then "✅ Notified" else "❌ Pending" end')
- **Affected Individuals:** $(echo "$breach" | jq -r 'if .notification_sent then "✅ Notified" else "❌ Pending" end')

---

## 6. Timeline

- **Breach Detected:** $(echo "$breach" | jq -r '.timestamp')
- **Breach Registered:** $(echo "$breach" | jq -r '.timestamp')
- **DPA Notification Deadline:** $(date -u -d "$(echo "$breach" | jq -r '.timestamp') + 72 hours" +"%Y-%m-%d %H:%M:%S UTC" 2>/dev/null || echo "72 hours from detection")

---

*This notification is generated in compliance with GDPR Articles 33 and 34*
EOF

  echo "✅ Notificação gerada: $output_file"
}

###############################################################################
# Lista violações registradas
###############################################################################
list_breaches() {
  if [[ ! -f "$BREACH_LOG" ]]; then
    echo "📋 Nenhuma violação registrada"
    return 0
  fi

  echo "📋 Violações de Dados Registradas"
  echo "=================================="

  jq -r '"ID: \(.breach_id) | Data: \(.timestamp) | Tipo: \(.type) | Severidade: \(.severity) | Status: \(.status)"' "$BREACH_LOG"
  echo ""
  echo "Total: $(jq -s 'length' "$BREACH_LOG")"
}

###############################################################################
# Atualiza status de violação
###############################################################################
update_breach_status() {
  local breach_id="$1"
  local new_status="$2"
  local remediation_step="${3:-}"

  if [[ ! -f "$BREACH_LOG" ]]; then
    echo "❌ Log de violações não encontrado" >&2
    return 1
  fi

  # Criar backup
  cp "$BREACH_LOG" "${BREACH_LOG}.bak"

  # Atualizar status
  jq --arg id "$breach_id" \
     --arg status "$new_status" \
     --arg step "$remediation_step" \
     --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    'if .breach_id == $id then
        .status = $status |
        .last_updated = $ts |
        (if $step != "" then .remediation_steps += [$step] else . end)
      else . end' \
    "$BREACH_LOG" > "${BREACH_LOG}.tmp"

  mv "${BREACH_LOG}.tmp" "$BREACH_LOG"

  echo "✅ Status atualizado: $breach_id → $new_status"
}

###############################################################################
# Modo de uso
###############################################################################
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-help}" in
    register)
      register_breach "${2:?Type required}" "${3:?Description required}" "${4:-unknown}" "${5:-high}"
      ;;
    notify)
      generate_notification "${2:?Breach ID required}"
      ;;
    list)
      list_breaches
      ;;
    update)
      update_breach_status "${2:?Breach ID required}" "${3:?New status required}" "${4:-}"
      ;;
    *)
      echo "Uso: $0 {register|notify|list|update} [args]"
      echo ""
      echo "Comandos:"
      echo "  register <type> <description> [affected_users] [severity]"
      echo "  notify <breach_id>"
      echo "  list"
      echo "  update <breach_id> <new_status> [remediation_step]"
      echo ""
      echo "Exemplos:"
      echo "  $0 register 'Unauthorized access' 'Sandbox escape attempt' '0' 'critical'"
      echo "  $0 notify BREACH-20251204-143022"
      echo "  $0 update BREACH-20251204-143022 'resolved' 'Security patch applied'"
      exit 1
      ;;
  esac
fi
