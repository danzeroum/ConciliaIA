import { getRedeCaptureType, getRedeProduct, getRedeService, getRedeStatus } from './rede-reference-tables';

export const REDE_EEVC_RECORD_LENGTH = 1024;

export type MonetaryAmount = number;

export interface RedeRegistro002Header {
  tipoRegistro: '002';
  dataArquivo: Date | null;
  horaArquivo: string;
  numeroPV: string;
  numeroPVGrupo: string;
  nomeEstabelecimento: string;
  sequenciaArquivo: string;
  versaoLayout: string;
}

export interface RedeRegistro005Request {
  tipoRegistro: '005';
  numeroPV: string;
  dataRequest: Date | null;
  codigoMotivo: string;
  valorRequest: MonetaryAmount;
  numeroCartao: string;
  nsuOriginal: string;
  numeroProcesso: string;
}

interface RedeRegistro008Fields {
  numeroPV: string;
  numeroRV: string;
  dataCVNSU: Date | null;
  valorCVNSU: MonetaryAmount;
  numeroCartao: string;
  statusCVNSU: string;
  numeroCVNSU: string;
  numeroAutorizacao: string;
  tipoCaptura: string;
  numeroTerminal: string;
  bandeira: string;
  codigoServico: string;
}

export interface RedeRegistro008 extends RedeRegistro008Fields {
  tipoRegistro: '008';
}

export interface RedeRegistro012 extends RedeRegistro008Fields {
  tipoRegistro: '012';
  numeroParcelas: number;
  valorPrimeiraParcela: MonetaryAmount;
  valorDemaisParcelas: MonetaryAmount;
}

export interface RedeRegistro028Trailer {
  tipoRegistro: '028';
  quantidadeRegistros: number;
  valorTotal: MonetaryAmount;
}

export interface RedeRegistro029ICPlus {
  tipoRegistro: '029';
  numeroPV: string;
  numeroRV: string;
  valorInterchange: MonetaryAmount;
  valorPlus: MonetaryAmount;
  mccTransacao: string;
  tipoCartao: string;
  modoEntrada: string;
}

export interface RedeECommerceTransaction extends RedeRegistro008Fields {
  tid: string;
  numeroPedido: string;
  indicadorAutenticacao: string;
  codigoAVS: string;
}

export type RedeRegistro033 = RedeECommerceTransaction & { tipoRegistro: '033' };
export type RedeRegistro034 = RedeECommerceTransaction & { tipoRegistro: '034' };
export type RedeRegistro035 = RedeECommerceTransaction & { tipoRegistro: '035' };
export type RedeRegistro036 = RedeECommerceTransaction & { tipoRegistro: '036' };

export type RedeRegistro =
  | RedeRegistro002Header
  | RedeRegistro005Request
  | RedeRegistro008
  | RedeRegistro012
  | RedeRegistro028Trailer
  | RedeRegistro029ICPlus
  | RedeRegistro033
  | RedeRegistro034
  | RedeRegistro035
  | RedeRegistro036;

function ensureRecordLength(line: string): void {
  if (line.length !== REDE_EEVC_RECORD_LENGTH) {
    throw new Error(`Tamanho de registro inválido: esperado ${REDE_EEVC_RECORD_LENGTH}, recebido ${line.length}`);
  }
}

function slice(line: string, start: number, end: number): string {
  if (start >= line.length) {
    return '';
  }
  return line.substring(start, Math.min(end, line.length));
}

function parseImpliedDecimal(value: string, decimalPlaces = 2): MonetaryAmount {
  const trimmed = value.trim();
  if (!trimmed) {
    return 0;
  }
  const negative = trimmed.startsWith('-') || trimmed.endsWith('-');
  const digits = trimmed.replace(/[^0-9]/g, '');
  if (!digits) {
    return 0;
  }
  const parsed = parseInt(digits, 10);
  const divisor = 10 ** decimalPlaces;
  const result = parsed / divisor;
  return negative ? -result : result;
}

function parseDate(value: string): Date | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  if (trimmed.length !== 8) {
    return null;
  }
  const day = parseInt(trimmed.substring(0, 2), 10);
  const month = parseInt(trimmed.substring(2, 4), 10);
  const year = parseInt(trimmed.substring(4, 8), 10);
  if (Number.isNaN(day) || Number.isNaN(month) || Number.isNaN(year)) {
    return null;
  }
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
    return null;
  }
  return date;
}

function parseInteger(value: string): number {
  const trimmed = value.trim();
  if (!trimmed) {
    return 0;
  }
  const parsed = parseInt(trimmed, 10);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function parseRegistro002(line: string): RedeRegistro002Header {
  ensureRecordLength(line);
  return {
    tipoRegistro: '002',
    dataArquivo: parseDate(slice(line, 3, 11)),
    horaArquivo: slice(line, 11, 15).trim(),
    numeroPV: slice(line, 15, 24).trim(),
    numeroPVGrupo: slice(line, 24, 33).trim(),
    nomeEstabelecimento: slice(line, 33, 83).trim(),
    sequenciaArquivo: slice(line, 83, 93).trim(),
    versaoLayout: slice(line, 93, 99).trim(),
  };
}

function parseRegistro005(line: string): RedeRegistro005Request {
  ensureRecordLength(line);
  return {
    tipoRegistro: '005',
    numeroPV: slice(line, 3, 12).trim(),
    dataRequest: parseDate(slice(line, 12, 20)),
    codigoMotivo: slice(line, 20, 24).trim(),
    valorRequest: parseImpliedDecimal(slice(line, 24, 39), 2),
    numeroCartao: slice(line, 39, 55).trim(),
    nsuOriginal: slice(line, 55, 67).trim(),
    numeroProcesso: slice(line, 67, 83).trim(),
  };
}

function parseRegistro008Fields(line: string): RedeRegistro008Fields {
  ensureRecordLength(line);
  const fields: RedeRegistro008Fields = {
    numeroPV: slice(line, 3, 12).trim(),
    numeroRV: slice(line, 12, 21).trim(),
    dataCVNSU: parseDate(slice(line, 21, 29)),
    valorCVNSU: parseImpliedDecimal(slice(line, 37, 52), 2),
    numeroCartao: slice(line, 67, 83).trim(),
    statusCVNSU: slice(line, 83, 86).trim(),
    numeroCVNSU: slice(line, 86, 98).trim(),
    numeroAutorizacao: slice(line, 126, 132).trim(),
    tipoCaptura: slice(line, 202, 203).trim(),
    numeroTerminal: slice(line, 218, 226).trim(),
    bandeira: slice(line, 229, 230).trim(),
    codigoServico: slice(line, 260, 263).trim(),
  };

  const status = getRedeStatus(fields.statusCVNSU);
  if (!status) {
    throw new Error(`Status CV/NSU desconhecido: ${fields.statusCVNSU}`);
  }

  const captureType = getRedeCaptureType(fields.tipoCaptura);
  if (!captureType) {
    throw new Error(`Tipo de captura inválido: ${fields.tipoCaptura}`);
  }

  const product = getRedeProduct(fields.bandeira);
  if (!product) {
    throw new Error(`Bandeira desconhecida: ${fields.bandeira}`);
  }

  const service = getRedeService(fields.codigoServico);
  if (!service) {
    throw new Error(`Código de serviço inválido: ${fields.codigoServico}`);
  }

  return fields;
}

function parseRegistro008(line: string): RedeRegistro008 {
  const fields = parseRegistro008Fields(line);
  return {
    tipoRegistro: '008',
    ...fields,
  };
}

function parseRegistro012(line: string): RedeRegistro012 {
  const base = parseRegistro008Fields(line);
  return {
    tipoRegistro: '012',
    ...base,
    numeroParcelas: parseInteger(slice(line, 203, 206)),
    valorPrimeiraParcela: parseImpliedDecimal(slice(line, 310, 325), 2),
    valorDemaisParcelas: parseImpliedDecimal(slice(line, 325, 340), 2),
  };
}

function parseRegistro028(line: string): RedeRegistro028Trailer {
  ensureRecordLength(line);
  return {
    tipoRegistro: '028',
    quantidadeRegistros: parseInteger(slice(line, 3, 9)),
    valorTotal: parseImpliedDecimal(slice(line, 9, 24), 2),
  };
}

function parseRegistro029(line: string): RedeRegistro029ICPlus {
  ensureRecordLength(line);
  return {
    tipoRegistro: '029',
    numeroPV: slice(line, 3, 12).trim(),
    numeroRV: slice(line, 12, 21).trim(),
    valorInterchange: parseImpliedDecimal(slice(line, 21, 36), 2),
    valorPlus: parseImpliedDecimal(slice(line, 36, 51), 2),
    mccTransacao: slice(line, 51, 55).trim(),
    tipoCartao: slice(line, 55, 56).trim(),
    modoEntrada: slice(line, 56, 57).trim(),
  };
}

function parseEcommerceRegistro<T extends '033' | '034' | '035' | '036'>(
  line: string,
  tipo: T,
): RedeECommerceTransaction & { tipoRegistro: T } {
  const base = parseRegistro008Fields(line);
  const ecommerce: RedeECommerceTransaction & { tipoRegistro: T } = {
    tipoRegistro: tipo,
    ...base,
    tid: slice(line, 340, 360).trim(),
    numeroPedido: slice(line, 360, 390).trim(),
    indicadorAutenticacao: slice(line, 390, 391).trim(),
    codigoAVS: slice(line, 391, 392).trim(),
  };
  return ecommerce;
}

export class RedeEEVCParser {
  parse(line: string): RedeRegistro {
    const tipo = slice(line, 0, 3);
    switch (tipo) {
      case '002':
        return parseRegistro002(line);
      case '005':
        return parseRegistro005(line);
      case '008':
        return parseRegistro008(line);
      case '012':
        return parseRegistro012(line);
      case '028':
        return parseRegistro028(line);
      case '029':
        return parseRegistro029(line);
      case '033':
        return parseEcommerceRegistro(line, '033');
      case '034':
        return parseEcommerceRegistro(line, '034');
      case '035':
        return parseEcommerceRegistro(line, '035');
      case '036':
        return parseEcommerceRegistro(line, '036');
      default:
        throw new Error(`Tipo de registro não suportado: ${tipo}`);
    }
  }

  parseRegistro002(line: string): RedeRegistro002Header {
    return parseRegistro002(line);
  }

  parseRegistro005(line: string): RedeRegistro005Request {
    return parseRegistro005(line);
  }

  parseRegistro008(line: string): RedeRegistro008 {
    return parseRegistro008(line);
  }

  parseRegistro012(line: string): RedeRegistro012 {
    return parseRegistro012(line);
  }

  parseRegistro028(line: string): RedeRegistro028Trailer {
    return parseRegistro028(line);
  }

  parseRegistro029(line: string): RedeRegistro029ICPlus {
    return parseRegistro029(line);
  }

  parseRegistro033(line: string): RedeRegistro033 {
    return parseEcommerceRegistro(line, '033');
  }

  parseRegistro034(line: string): RedeRegistro034 {
    return parseEcommerceRegistro(line, '034');
  }

  parseRegistro035(line: string): RedeRegistro035 {
    return parseEcommerceRegistro(line, '035');
  }

  parseRegistro036(line: string): RedeRegistro036 {
    return parseEcommerceRegistro(line, '036');
  }
}
