import { apiClient } from './axios-config';
import type {
  Sale,
  CreateSaleRequest,
  UpdateSaleRequest,
  PaginatedResponse,
  SalesFilters,
  ImportSalesResponse,
} from '@/types/api.types';

const sanitizeParams = (params: Record<string, unknown>) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) =>
      value !== undefined && value !== null && value !== ''
    )
  );

export const salesApi = {
  async getSales(filters: SalesFilters = {}): Promise<PaginatedResponse<Sale>> {
    const params = sanitizeParams({
      start_date: filters.startDate,
      end_date: filters.endDate,
      status: filters.status,
      search: filters.search,
      page: filters.page ?? 1,
      page_size: filters.pageSize ?? 50,
    });

    const response = await apiClient.get<PaginatedResponse<Sale>>('/api/sales', {
      params,
    });
    return response.data;
  },

  async getSaleById(id: string): Promise<Sale> {
    const response = await apiClient.get<Sale>(`/api/sales/${id}`);
    return response.data;
  },

  async createSale(data: CreateSaleRequest): Promise<Sale> {
    const response = await apiClient.post<Sale>('/api/sales', data);
    return response.data;
  },

  async updateSale(id: string, data: UpdateSaleRequest): Promise<Sale> {
    const response = await apiClient.put<Sale>(`/api/sales/${id}`, data);
    return response.data;
  },

  async deleteSale(id: string): Promise<void> {
    await apiClient.delete(`/api/sales/${id}`);
  },

  async importSales(file: File): Promise<ImportSalesResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ImportSalesResponse>(
      '/api/sales/import',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  async exportSales(filters: SalesFilters = {}): Promise<Blob> {
    const params = sanitizeParams({
      start_date: filters.startDate,
      end_date: filters.endDate,
      status: filters.status,
    });

    const response = await apiClient.get<BlobPart>('/api/sales/export', {
      params,
      responseType: 'blob',
    });
    return response.data as Blob;
  },
};
