import { apiClient } from './axios-config';

export interface Transaction {
  id: string;
  tenant_id: string;
  nsu: string;
  acquirer: string;
  amount: number;
  transaction_date: string;
  settlement_date: string | null;
  card_brand: string;
  authorization_code: string | null;
  mdr_rate: number | null;
  mdr_amount: number | null;
  installments: number;
  terminal_id: string | null;
  merchant_id: string | null;
  matched: boolean;
  match_id: string | null;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionRequest {
  nsu: string;
  acquirer: string;
  amount: number;
  transaction_date: string;
  settlement_date?: string;
  card_brand: string;
  authorization_code?: string;
  mdr_rate?: number;
  mdr_amount?: number;
  installments?: number;
  terminal_id?: string;
  merchant_id?: string;
  metadata?: Record<string, any>;
}

export interface TransactionsListResponse {
  items: Transaction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ImportTransactionsResponse {
  imported: number;
  failed: number;
  errors?: Array<{ row: number; error: string; data: any }>;
}

export const transactionsApi = {
  // List transactions
  list: async (params?: {
    start_date?: string;
    end_date?: string;
    acquirer?: string;
    matched?: boolean;
    nsu?: string;
    page?: number;
    page_size?: number;
  }): Promise<TransactionsListResponse> => {
    const response = await apiClient.get('/api/v1/transactions', { params });
    return response.data;
  },

  // Get transaction by ID
  getById: async (id: string): Promise<Transaction> => {
    const response = await apiClient.get(`/api/v1/transactions/${id}`);
    return response.data;
  },

  // Create transaction
  create: async (data: CreateTransactionRequest): Promise<Transaction> => {
    const response = await apiClient.post('/api/v1/transactions', data);
    return response.data;
  },

  // Delete transaction
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/transactions/${id}`);
  },

  // Import from CSV
  importCSV: async (file: File): Promise<ImportTransactionsResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/v1/transactions/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Export to CSV
  exportCSV: async (params?: { start_date?: string; end_date?: string }): Promise<Blob> => {
    const response = await apiClient.get('/api/v1/transactions/export/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};
