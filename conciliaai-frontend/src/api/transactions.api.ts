import { apiClient } from './axios-config';
import type {
  Transaction,
  PaginatedResponse,
  ImportTransactionsResponse,
} from '@/types/api.types';

export interface TransactionsFilters {
  startDate?: string;
  endDate?: string;
  acquirer?: string;
  status?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}

const sanitizeParams = (params: Record<string, unknown>) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) =>
      value !== undefined && value !== null && value !== ''
    )
  );

export const transactionsApi = {
  async getTransactions(
    filters: TransactionsFilters = {}
  ): Promise<PaginatedResponse<Transaction>> {
    const params = sanitizeParams({
      start_date: filters.startDate,
      end_date: filters.endDate,
      acquirer: filters.acquirer,
      status: filters.status,
      search: filters.search,
      page: filters.page ?? 1,
      page_size: filters.pageSize ?? 50,
    });

    const response = await apiClient.get<PaginatedResponse<Transaction>>(
      '/api/transactions',
      {
        params,
      }
    );
    return response.data;
  },

  async getTransactionById(id: string): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/api/transactions/${id}`);
    return response.data;
  },

  async importFromAcquirer(
    acquirer: string,
    startDate: string,
    endDate: string
  ): Promise<ImportTransactionsResponse> {
    const response = await apiClient.post<ImportTransactionsResponse>(
      '/api/transactions/import',
      {
        acquirer,
        start_date: startDate,
        end_date: endDate,
      }
    );
    return response.data;
  },
};
