export type PaymentMethod = 'credit' | 'debit' | 'pix' | 'voucher' | string;

export type Acquirer = 'cielo' | 'rede' | 'stone' | string;

export type DivergenceSeverity = 'critical' | 'high' | 'medium' | 'low';

export type MatchStatus = 'matched' | 'unmatched';

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

export interface DateRangeFilter {
  start_date?: string;
  end_date?: string;
}
