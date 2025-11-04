export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export enum PaymentMethod {
  CREDIT = 'credit',
  DEBIT = 'debit',
  PIX = 'pix',
  VOUCHER = 'voucher',
}

export type PaymentMethodValue = `${PaymentMethod}` | (string & {});

export type Acquirer = 'cielo' | 'rede' | 'stone' | (string & {});

export enum DivergenceType {
  AMOUNT_MISMATCH = 'amount_mismatch',
  DATE_MISMATCH = 'date_mismatch',
  MISSING_SALE = 'missing_sale',
  MISSING_TRANSACTION = 'missing_transaction',
  INSTALLMENT_MISMATCH = 'installment_mismatch',
  MDR_VARIANCE = 'mdr_variance',
}

export enum Severity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export type DivergenceSeverity = `${Severity}`;

export type MatchStatus = 'matched' | 'unmatched';
