import {
  getRedeRequestReason,
  getRedeStatus,
  REDE_ADJUSTMENT_CODES,
  REDE_REQUEST_REASON_CODES,
  REDE_STATUS_CODES,
} from './rede-reference-tables';
import {
  MonetaryAmount,
  RedeRegistro005Request,
  RedeRegistro008,
  RedeRegistro012,
  RedeRegistro029ICPlus,
  RedeRegistro033,
  RedeRegistro034,
  RedeRegistro035,
  RedeRegistro036,
} from './rede-eevc-parser';

export interface ValidationResult {
  valid: boolean;
  reason?: string;
  code?: string;
}

export interface ParcelamentoBreakdown {
  numeroParcelas: number;
  valorPrimeiraParcela: MonetaryAmount;
  valorDemaisParcelas: MonetaryAmount;
  valorTotalCalculado: MonetaryAmount;
}

const CHARGEBACK_CODES = new Set<string>([
  '3001',
  '3002',
  '3003',
  '3040',
  '3053',
  '3055',
  '3059',
  '3060',
  '3097',
  '3140',
]);

export function isChargeback(code: string): boolean {
  const normalized = code.trim();
  if (!normalized) {
    return false;
  }
  if (CHARGEBACK_CODES.has(normalized)) {
    return true;
  }
  const reference = getRedeRequestReason(normalized);
  return reference?.category === 'CHARGEBACK';
}

export function validateStatus(record: RedeRegistro008): ValidationResult {
  const status = getRedeStatus(record.statusCVNSU);
  if (!status) {
    return { valid: false, reason: 'Status não mapeado', code: record.statusCVNSU };
  }
  if (status.severity === 'REJECTION') {
    return { valid: false, reason: status.description, code: status.code };
  }
  return { valid: true };
}

export function validateAutenticacao(
  record: RedeRegistro033 | RedeRegistro034 | RedeRegistro035 | RedeRegistro036,
): ValidationResult {
  const indicador = record.indicadorAutenticacao.trim();
  if (!indicador) {
    return { valid: false, reason: 'Transação e-commerce sem indicador de autenticação' };
  }
  if (indicador === 'N' || indicador === '0') {
    return { valid: false, reason: 'Autenticação não realizada', code: indicador };
  }
  return { valid: true };
}

export function validateParcelamento(record: RedeRegistro012): ValidationResult {
  if (record.numeroParcelas <= 0) {
    return { valid: false, reason: 'Quantidade de parcelas inválida', code: String(record.numeroParcelas) };
  }
  if (record.numeroParcelas > 12) {
    return { valid: false, reason: 'Parcelas excedem limite', code: String(record.numeroParcelas) };
  }
  const totalCalculado =
    record.valorPrimeiraParcela + record.valorDemaisParcelas * (record.numeroParcelas - 1);
  const diff = Math.abs(totalCalculado - record.valorCVNSU);
  if (diff > 0.01) {
    return { valid: false, reason: 'Divergência no valor de parcelas' };
  }
  return { valid: true };
}

export function buildParcelamentoBreakdown(record: RedeRegistro012): ParcelamentoBreakdown {
  const valorTotalCalculado =
    record.valorPrimeiraParcela + record.valorDemaisParcelas * (record.numeroParcelas - 1);
  return {
    numeroParcelas: record.numeroParcelas,
    valorPrimeiraParcela: record.valorPrimeiraParcela,
    valorDemaisParcelas: record.valorDemaisParcelas,
    valorTotalCalculado,
  };
}

export function validateRequestRecord(record: RedeRegistro005Request): ValidationResult {
  const motivo = getRedeRequestReason(record.codigoMotivo);
  if (!motivo) {
    return { valid: false, reason: 'Motivo de request inválido', code: record.codigoMotivo };
  }
  if (isChargeback(record.codigoMotivo) && record.valorRequest <= 0) {
    return { valid: false, reason: 'Chargeback sem valor associado' };
  }
  return { valid: true };
}

export function evaluateICPlus(record: RedeRegistro029ICPlus): MonetaryAmount {
  return record.valorInterchange + record.valorPlus;
}

export function validateAdjustmentCode(code: string): ValidationResult {
  const normalized = code.trim();
  if (!normalized) {
    return { valid: false, reason: 'Código de ajuste vazio' };
  }
  if (!REDE_ADJUSTMENT_CODES[normalized]) {
    return { valid: false, reason: 'Código de ajuste não reconhecido', code: normalized };
  }
  return { valid: true };
}

export function getRequestCategory(code: string): string | undefined {
  const reason = getRedeRequestReason(code);
  return reason?.category;
}

export function requiresDocumentation(code: string): boolean {
  const reason = getRedeRequestReason(code);
  if (!reason) {
    return false;
  }
  return reason.category === 'DOCUMENTATION' || reason.category === 'CHARGEBACK';
}

export function getStatusSummary(): Array<{ code: string; description: string; severity: string }> {
  return Object.values(REDE_STATUS_CODES).map((status) => ({
    code: status.code,
    description: status.description,
    severity: status.severity,
  }));
}

export function getRequestReasonsSummary(): Array<{ code: string; description: string }> {
  return Object.values(REDE_REQUEST_REASON_CODES).map((reason) => ({
    code: reason.code,
    description: reason.description,
  }));
}
