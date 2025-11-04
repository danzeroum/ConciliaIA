import { apiClient } from './axios-config';

export interface Sale {
  id: string;
  tenant_id: string;
  nsu: string;
  amount: number;
  sale_date: string;
  payment_method: string;
  installments: number;
  card_brand: string | null;
  authorization_code: string | null;
  pos_terminal_id: string | null;
  merchant_id: string | null;
  matched: boolean;
  match_id: string | null;
  customer_document: string | null;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CreateSaleRequest {
  nsu: string;
  amount: number;
  sale_date: string;
  payment_method: string;
  installments?: number;
  card_brand?: string;
  authorization_code?: string;
  pos_terminal_id?: string;
  merchant_id?: string;
  customer_document?: string;
  metadata?: Record<string, any>;
}

export interface SalesListResponse {
  items: Sale[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ImportSalesResponse {
  imported: number;
  failed: number;
  errors: Array<{ row: number; error: string; data: any }>;
}

export const salesApi = {
  // List sales
  list: async (params?: {
    start_date?: string;
    end_date?: string;
    payment_method?: string;
    matched?: boolean;
    nsu?: string;
    page?: number;
    page_size?: number;
  }): Promise<SalesListResponse> => {
    const normalizedParams = params
      ? {
          ...params,
          matched: params.matched ?? undefined,
        }
      : undefined;

    const response = await apiClient.get('/api/v1/sales', {
      params: normalizedParams,
    });
    return response.data;
  },

  // Get sale by ID
  getById: async (id: string): Promise<Sale> => {
    const response = await apiClient.get(`/api/v1/sales/${id}`);
    return response.data;
  },

  // Create sale
  create: async (data: CreateSaleRequest): Promise<Sale> => {
    const response = await apiClient.post('/api/v1/sales', data);
    return response.data;
  },

  // Update sale
  update: async (id: string, data: Partial<CreateSaleRequest>): Promise<Sale> => {
    const response = await apiClient.put(`/api/v1/sales/${id}`, data);
    return response.data;
  },

  // Delete sale
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/sales/${id}`);
  },

  // Import from CSV
  importCSV: async (file: File): Promise<ImportSalesResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/api/v1/sales/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Export to CSV
  exportCSV: async (params?: { start_date?: string; end_date?: string }): Promise<Blob> => {
    const response = await apiClient.get('/api/v1/sales/export/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};
