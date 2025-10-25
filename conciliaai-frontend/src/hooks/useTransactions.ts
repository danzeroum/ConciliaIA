import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  transactionsApi,
  CreateTransactionRequest,
  ImportTransactionsResponse,
} from '@/api/transactions.api';
import { useUIStore } from '@/store/ui.store';

export function useTransactions(params?: {
  start_date?: string;
  end_date?: string;
  acquirer?: string;
  matched?: boolean;
  nsu?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['transactions', params],
    queryFn: () => transactionsApi.list(params),
  });
}

export function useTransaction(id: string) {
  return useQuery({
    queryKey: ['transactions', id],
    queryFn: () => transactionsApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (data: CreateTransactionRequest) => transactionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      showNotification('Transação criada com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao criar transação',
        'error'
      );
    },
  });
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (id: string) => transactionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      showNotification('Transação excluída com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao excluir transação',
        'error'
      );
    },
  });
}

export function useImportTransactions() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (file: File): Promise<ImportTransactionsResponse> =>
      transactionsApi.importCSV(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      showNotification(
        `${data.imported} transações importadas. ${data.failed} falharam.`,
        data.failed > 0 ? 'warning' : 'success'
      );
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao importar transações',
        'error'
      );
    },
  });
}


export function useImportTransactionsEDI() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, acquirer }: { file: File; acquirer?: string }) =>
      transactionsApi.importEDI(file, acquirer || 'rede'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['kpis'] });
    },
  });
}

export function useExportTransactions() {
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (params?: { start_date?: string; end_date?: string }) =>
      transactionsApi.exportCSV(params),
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transactions_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showNotification('Transações exportadas com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao exportar transações',
        'error'
      );
    },
  });
}
