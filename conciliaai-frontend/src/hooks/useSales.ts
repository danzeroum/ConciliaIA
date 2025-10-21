import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesApi, CreateSaleRequest } from '@/api/sales.api';
import { useUIStore } from '@/store/ui.store';

export function useSales(params?: {
  start_date?: string;
  end_date?: string;
  payment_method?: string;
  matched?: boolean;
  nsu?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['sales', params],
    queryFn: () => salesApi.list(params),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useSale(id: string) {
  return useQuery({
    queryKey: ['sales', id],
    queryFn: () => salesApi.getById(id),
    enabled: !!id,
  });
}

export function useCreateSale() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (data: CreateSaleRequest) => salesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      showNotification('Venda criada com sucesso', 'success');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Erro ao criar venda';
      showNotification(message, 'error');
    },
  });
}

export function useUpdateSale() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateSaleRequest> }) =>
      salesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      if (variables?.id) {
        queryClient.invalidateQueries({ queryKey: ['sales', variables.id] });
      }
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      showNotification('Venda atualizada com sucesso', 'success');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Erro ao atualizar venda';
      showNotification(message, 'error');
    },
  });
}

export function useDeleteSale() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (id: string) => salesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      showNotification('Venda excluída com sucesso', 'success');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Erro ao excluir venda';
      showNotification(message, 'error');
    },
  });
}

export function useImportSales() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (file: File) => salesApi.importCSV(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });

      if (data.failed > 0) {
        showNotification(
          `${data.imported} vendas importadas, ${data.failed} falhas. Verifique os erros.`,
          'warning'
        );
      } else {
        showNotification(`${data.imported} vendas importadas com sucesso`, 'success');
      }
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Erro ao importar vendas';
      showNotification(message, 'error');
    },
  });
}

export function useExportSales() {
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (params?: { start_date?: string; end_date?: string }) =>
      salesApi.exportCSV(params),
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vendas_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showNotification('Exportação de vendas concluída', 'success');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Erro ao exportar vendas';
      showNotification(message, 'error');
    },
  });
}
