import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsApi, TransactionsFilters } from '@/api/transactions.api';
import { useNotifications } from './useNotifications';
import type {
  Transaction,
  PaginatedResponse,
  ImportTransactionsResponse,
} from '@/types/api.types';

export function useTransactions(filters?: TransactionsFilters) {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  const transactionsQuery = useQuery<
    PaginatedResponse<Transaction>,
    Error,
    PaginatedResponse<Transaction>
  >({
    queryKey: ['transactions', filters],
    queryFn: () => transactionsApi.getTransactions(filters ?? {}),
    staleTime: 5 * 60 * 1000,
  });

  const useTransactionById = (id: string) =>
    useQuery<Transaction, Error>({
      queryKey: ['transactions', id],
      queryFn: () => transactionsApi.getTransactionById(id),
      enabled: Boolean(id),
      staleTime: 5 * 60 * 1000,
    });

  const importMutation = useMutation<
    ImportTransactionsResponse,
    any,
    { acquirer: string; startDate: string; endDate: string }
  >({
    mutationFn: ({ acquirer, startDate, endDate }) =>
      transactionsApi.importFromAcquirer(acquirer, startDate, endDate),
    onSuccess: (data) => {
      showSuccess(`${data.imported} transações importadas com sucesso!`);
      if (data.errors > 0) {
        showError(`${data.errors} transações com erro.`);
      }
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
    onError: (error: any) => {
      showError(error?.response?.data?.message || 'Erro ao importar transações.');
    },
  });

  return {
    transactions: transactionsQuery.data?.results ?? [],
    totalTransactions: transactionsQuery.data?.total ?? 0,
    totalPages: transactionsQuery.data?.total_pages ?? 0,
    currentPage: transactionsQuery.data?.page ?? filters?.page ?? 1,
    pageSize: transactionsQuery.data?.page_size ?? filters?.pageSize ?? 50,

    isLoading: transactionsQuery.isLoading,
    isFetching: transactionsQuery.isFetching,
    isError: transactionsQuery.isError,
    error: transactionsQuery.error,

    importFromAcquirer: importMutation.mutate,
    isImporting: importMutation.isPending,

    refetch: transactionsQuery.refetch,
    useTransactionById,
  };
}
