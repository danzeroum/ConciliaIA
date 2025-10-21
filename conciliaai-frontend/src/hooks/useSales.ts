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
      showNotification('Venda criada com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao criar venda',
        'error'
      );
    },
  });
}

export function useUpdateSale() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateSaleRequest> }) =>
      salesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales'] });
      showNotification('Venda atualizada com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao atualizar venda',
        'error'
      );
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
      showNotification('Venda excluída com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao excluir venda',
        'error'
      );
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
      showNotification(
        `${data.imported} vendas importadas com sucesso. ${data.failed} falharam.`,
        data.failed > 0 ? 'warning' : 'success'
      );
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao importar vendas',
        'error'
      );
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
      a.download = `sales_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showNotification('Vendas exportadas com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao exportar vendas',
        'error'
      );
    },
  });
}
