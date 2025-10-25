/*
 * Reference tables extracted from the Rede EEVC (Extrato Eletrônico de Vendas Crédito)
 * technical specification. The goal of this module is to expose the lookup
 * structures in a TypeScript friendly format so that both parsers and higher
 * level business rules can consume the information in a deterministic way.
 */

export interface RedeReferenceEntry {
  code: string;
  description: string;
}

export interface RedeProduct extends RedeReferenceEntry {
  brand: string;
}

export interface RedeCaptureType extends RedeReferenceEntry {
  channel: 'PRESENTIAL' | 'ECOMMERCE' | 'MOTO' | 'MOBILE' | 'UNKNOWN';
}

export type RedeStatusSeverity = 'INFO' | 'ATTENTION' | 'REJECTION';

export interface RedeStatusCode extends RedeReferenceEntry {
  action: 'APPROVED' | 'PENDING' | 'REVIEW' | 'REJECTED';
  severity: RedeStatusSeverity;
}

export interface RedeRequestReason extends RedeReferenceEntry {
  category: 'CHARGEBACK' | 'DOCUMENTATION' | 'FRAUD' | 'OPERATIONAL' | 'OTHER';
}

export interface RedeAdjustmentCode extends RedeReferenceEntry {
  group: 'FINANCIAL' | 'OPERATIONAL' | 'PROMOTIONAL' | 'SERVICE' | 'OTHER';
}

export interface RedeServiceCode extends RedeReferenceEntry {
  area: 'FINANCIAL' | 'RISK' | 'LOGISTICS' | 'CHARGEBACK' | 'OTHER';
}

export interface RedeReferenceTables {
  products: Record<string, RedeProduct>;
  captureTypes: Record<string, RedeCaptureType>;
  status: Record<string, RedeStatusCode>;
  requestReasons: Record<string, RedeRequestReason>;
  adjustments: Record<string, RedeAdjustmentCode>;
  serviceCodes: Record<string, RedeServiceCode>;
}

export const REDE_PRODUCTS: RedeReferenceTables['products'] = {
  '0': { code: '0', description: 'Outras bandeiras', brand: 'OUTRAS' },
  '1': { code: '1', description: 'Mastercard crédito', brand: 'MASTERCARD' },
  '2': { code: '2', description: 'Diners Club', brand: 'DINERS' },
  '3': { code: '3', description: 'Visa crédito', brand: 'VISA' },
  '4': { code: '4', description: 'Cabal', brand: 'CABAL' },
  '5': { code: '5', description: 'Hipercard', brand: 'HIPERCARD' },
  '6': { code: '6', description: 'Sorocred', brand: 'SOROCRED' },
  '7': { code: '7', description: 'China Union Pay', brand: 'CUP' },
  '8': { code: '8', description: 'CredSystem', brand: 'CRED-SYSTEM' },
  '9': { code: '9', description: 'Sicredi', brand: 'SICREDI' },
  A: { code: 'A', description: 'Avista', brand: 'AVISTA' },
  B: { code: 'B', description: 'Banescard', brand: 'BANESCARD' },
  E: { code: 'E', description: 'Elo', brand: 'ELO' },
  J: { code: 'J', description: 'JCB', brand: 'JCB' },
  X: { code: 'X', description: 'American Express', brand: 'AMEX' },
  Z: { code: 'Z', description: 'Credz', brand: 'CREDZ' },
};

export const REDE_CAPTURE_TYPES: RedeReferenceTables['captureTypes'] = {
  '0': {
    code: '0',
    description: 'Captura presencial (POS/TEF)',
    channel: 'PRESENTIAL',
  },
  '1': {
    code: '1',
    description: 'E-commerce autenticado',
    channel: 'ECOMMERCE',
  },
  '2': {
    code: '2',
    description: 'Venda digitada (MOTO)',
    channel: 'MOTO',
  },
  '3': {
    code: '3',
    description: 'Aplicativo móvel / mPOS',
    channel: 'MOBILE',
  },
  '4': {
    code: '4',
    description: 'E-commerce sem autenticação',
    channel: 'ECOMMERCE',
  },
  '9': {
    code: '9',
    description: 'Canal não identificado',
    channel: 'UNKNOWN',
  },
};

export const REDE_STATUS_CODES: RedeReferenceTables['status'] = {
  '0': {
    code: '0',
    description: 'Transação autorizada',
    action: 'APPROVED',
    severity: 'INFO',
  },
  '1': {
    code: '1',
    description: 'Transação duplicada',
    action: 'REVIEW',
    severity: 'ATTENTION',
  },
  '10': {
    code: '10',
    description: 'Cartão bloqueado / Boletim de Ocorrência',
    action: 'REJECTED',
    severity: 'REJECTION',
  },
  '13': {
    code: '13',
    description: 'Venda sem autorização válida',
    action: 'REJECTED',
    severity: 'REJECTION',
  },
  '20': {
    code: '20',
    description: 'Transação confirmada, aguardando captura',
    action: 'PENDING',
    severity: 'ATTENTION',
  },
  '37': {
    code: '37',
    description: 'Apresentação tardia',
    action: 'REVIEW',
    severity: 'ATTENTION',
  },
  '65': {
    code: '65',
    description: 'Cartão com restrição',
    action: 'REJECTED',
    severity: 'REJECTION',
  },
  '75': {
    code: '75',
    description: 'Limite excedido',
    action: 'REJECTED',
    severity: 'REJECTION',
  },
  '80': {
    code: '80',
    description: 'Transação em disputa (request)',
    action: 'REVIEW',
    severity: 'ATTENTION',
  },
  '99': {
    code: '99',
    description: 'Erro operacional não tratado',
    action: 'REJECTED',
    severity: 'REJECTION',
  },
};

export const REDE_REQUEST_REASON_CODES: RedeReferenceTables['requestReasons'] = {
  '0017': {
    code: '0017',
    description: 'Documento ilegível ou ausente',
    category: 'DOCUMENTATION',
  },
  '3001': {
    code: '3001',
    description: 'Chargeback - Não reconhecimento da compra',
    category: 'CHARGEBACK',
  },
  '3002': {
    code: '3002',
    description: 'Chargeback - Serviços não prestados',
    category: 'CHARGEBACK',
  },
  '3053': {
    code: '3053',
    description: 'Chargeback - Ausência de comprovante',
    category: 'CHARGEBACK',
  },
  '3059': {
    code: '3059',
    description: 'Fraude - Chip/PIN não validado',
    category: 'FRAUD',
  },
  '3097': {
    code: '3097',
    description: 'Transação contestada pelo portador',
    category: 'CHARGEBACK',
  },
  '3140': {
    code: '3140',
    description: 'Serviço não prestado em e-commerce',
    category: 'CHARGEBACK',
  },
  '4005': {
    code: '4005',
    description: 'Processo operacional - Documentação incompleta',
    category: 'OPERATIONAL',
  },
  '9210': {
    code: '9210',
    description: 'Outros motivos operacionais',
    category: 'OTHER',
  },
};

export const REDE_ADJUSTMENT_CODES: RedeReferenceTables['adjustments'] = {
  '1': {
    code: '1',
    description: 'Reembolso total do valor da transação',
    group: 'FINANCIAL',
  },
  '2': {
    code: '2',
    description: 'Reembolso parcial / abatimento',
    group: 'FINANCIAL',
  },
  '5': {
    code: '5',
    description: 'Cobrança de taxas administrativas',
    group: 'SERVICE',
  },
  '8': {
    code: '8',
    description: 'Estorno operacional',
    group: 'OPERATIONAL',
  },
  '17': {
    code: '17',
    description: 'Campanha promocional',
    group: 'PROMOTIONAL',
  },
  '45': {
    code: '45',
    description: 'Complemento IC+',
    group: 'FINANCIAL',
  },
  '72': {
    code: '72',
    description: 'Despesas logísticas',
    group: 'SERVICE',
  },
  '99': {
    code: '99',
    description: 'Outros ajustes não especificados',
    group: 'OTHER',
  },
};

export const REDE_SERVICE_CODES: RedeReferenceTables['serviceCodes'] = {
  '001': { code: '001', description: 'Venda padrão', area: 'FINANCIAL' },
  '003': { code: '003', description: 'Captura antecipada', area: 'FINANCIAL' },
  '010': { code: '010', description: 'Serviço de prevenção a fraude', area: 'RISK' },
  '015': { code: '015', description: 'Logística integrada', area: 'LOGISTICS' },
  '101': { code: '101', description: 'Processamento de request', area: 'CHARGEBACK' },
  '220': { code: '220', description: 'Serviço IC+', area: 'FINANCIAL' },
  '310': { code: '310', description: 'Monitoramento AVS', area: 'RISK' },
  '999': { code: '999', description: 'Serviços diversos', area: 'OTHER' },
};

export const REDE_REFERENCE_TABLES: RedeReferenceTables = {
  products: REDE_PRODUCTS,
  captureTypes: REDE_CAPTURE_TYPES,
  status: REDE_STATUS_CODES,
  requestReasons: REDE_REQUEST_REASON_CODES,
  adjustments: REDE_ADJUSTMENT_CODES,
  serviceCodes: REDE_SERVICE_CODES,
};

export function getRedeProduct(code: string): RedeProduct | undefined {
  return REDE_PRODUCTS[code.trim()] ?? undefined;
}

export function getRedeCaptureType(code: string): RedeCaptureType | undefined {
  return REDE_CAPTURE_TYPES[code.trim()] ?? undefined;
}

export function getRedeStatus(code: string): RedeStatusCode | undefined {
  return REDE_STATUS_CODES[code.trim()] ?? undefined;
}

export function getRedeRequestReason(code: string): RedeRequestReason | undefined {
  return REDE_REQUEST_REASON_CODES[code.trim()] ?? undefined;
}

export function getRedeAdjustment(code: string): RedeAdjustmentCode | undefined {
  return REDE_ADJUSTMENT_CODES[code.trim()] ?? undefined;
}

export function getRedeService(code: string): RedeServiceCode | undefined {
  return REDE_SERVICE_CODES[code.trim()] ?? undefined;
}
