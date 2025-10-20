export type SaleStatus = 'matched' | 'unmatched' | 'pending';

export type PaymentMethod =
  | 'credit_card'
  | 'debit_card'
  | 'pix'
  | 'boleto'
  | string;

export interface Sale {
  id: string;
  tenant_id: string;
  nsu: string;
  amount: string;
  date: string;
  payment_method: PaymentMethod;
  status: SaleStatus;
  created_at: string;
  updated_at: string;
}

export type Acquirer = 'cielo' | 'rede' | 'stone' | string;

export interface Transaction {
  id: string;
  tenant_id: string;
  acquirer: Acquirer;
  nsu: string;
  amount: string;
  transaction_date: string;
  card_brand: string;
  card_last_4: string;
  mdr_rate: string;
  mdr_amount: string;
  net_amount: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CreateSaleRequest {
  nsu: string;
  amount: string;
  date: string;
  payment_method: PaymentMethod;
}

export interface UpdateSaleRequest extends Partial<CreateSaleRequest> {
  status?: SaleStatus;
}

export interface SalesFilters {
  startDate?: string;
  endDate?: string;
  status?: SaleStatus | '';
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface ImportSalesResponse {
  imported: number;
  errors: number;
  error_rows?: number[];
  message?: string;
}

export interface ImportTransactionsResponse {
  imported: number;
  errors: number;
  message?: string;
}
