import { useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesApi } from '@/api/sales.api';
import { useNotifications } from './useNotifications';
import type {
  SalesFilters,
  CreateSaleRequest,
  UpdateSaleRequest,
  Sale,
  PaginatedResponse,
  ImportSalesResponse,
} from '@/types/api.types';

export function useSales(filters?: SalesFilters) {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  const salesQuery = useQuery<
    PaginatedResponse<Sale>,
    Error,
    PaginatedResponse<Sale>
  >({
    queryKey: ['sales', filters],
    queryFn: () => salesApi.getSales(filters ?? {}),
    staleTime: 5 * 60 * 1000,
  });

  const useSaleById = (id: string) =>
    useQuery<Sale, Error>({
      queryKey: ['sales', id],
      queryFn: () => salesApi.getSaleById(id),
      enabled: Boolean(id),
      staleTime: 5 * 60 * 1000,
    });

  const createSaleMutation = useMutation<Sale, any, CreateSaleRequest>({
    mutationFn: (data) => salesApi.createSale(data),
    onSuccess: () => {
      showSuccess('Venda criada com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: (error: any) => {
      showError(error?.response?.data?.message || 'Erro ao criar venda.');
    },
  });

  const updateSaleMutation = useMutation<
    Sale,
    any,
    { id: string; data: UpdateSaleRequest }
  >({
    mutationFn: ({ id, data }) => salesApi.updateSale(id, data),
    onSuccess: () => {
      showSuccess('Venda atualizada com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: (error: any) => {
      showError(error?.response?.data?.message || 'Erro ao atualizar venda.');
    },
  });

  const deleteSaleMutation = useMutation<void, any, string>({
    mutationFn: (id) => salesApi.deleteSale(id),
    onSuccess: () => {
      showSuccess('Venda excluída com sucesso!');
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: (error: any) => {
      showError(error?.response?.data?.message || 'Erro ao excluir venda.');
    },
  });

  const importSalesMutation = useMutation<ImportSalesResponse, any, File>({
    mutationFn: (file) => salesApi.importSales(file),
    onSuccess: (data) => {
      showSuccess(`${data.imported} vendas importadas com sucesso!`);
      if (data.errors > 0) {
        showError(`${data.errors} vendas com erro.`);
      }
      queryClient.invalidateQueries({ queryKey: ['sales'] });
    },
    onError: (error: any) => {
      showError(error?.response?.data?.message || 'Erro ao importar vendas.');
    },
  });

  const exportSales = useCallback(async () => {
    try {
      const blob = await salesApi.exportSales(filters);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `vendas_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(anchor);
      showSuccess('Vendas exportadas com sucesso!');
    } catch (error: any) {
      showError(error?.response?.data?.message || 'Erro ao exportar vendas.');
    }
  }, [filters, showError, showSuccess]);

  return {
    sales: salesQuery.data?.results ?? [],
    totalSales: salesQuery.data?.total ?? 0,
    totalPages: salesQuery.data?.total_pages ?? 0,
    currentPage: salesQuery.data?.page ?? filters?.page ?? 1,
    pageSize: salesQuery.data?.page_size ?? filters?.pageSize ?? 50,

    isLoading: salesQuery.isLoading,
    isFetching: salesQuery.isFetching,
    isError: salesQuery.isError,
    error: salesQuery.error,

    createSale: createSaleMutation.mutate,
    updateSale: updateSaleMutation.mutate,
    deleteSale: deleteSaleMutation.mutate,
    importSales: importSalesMutation.mutate,
    exportSales,

    isCreating: createSaleMutation.isPending,
    isUpdating: updateSaleMutation.isPending,
    isDeleting: deleteSaleMutation.isPending,
    isImporting: importSalesMutation.isPending,

    refetch: salesQuery.refetch,
    useSaleById,
  };
}
