import { useMutation } from '@tanstack/react-query';
import { saveAs } from 'file-saver';
import { apiClient } from '@/api/axios-config';
import { useUIStore } from '@/store/ui.store';

export const exportApi = {
  exportSalesExcel: async (params?: { start_date?: string; end_date?: string }) => {
    const response = await apiClient.get('/api/v1/export/sales/excel', {
      params,
      responseType: 'blob',
    });
    return response.data as Blob;
  },
  exportAccuracyReportExcel: async (start_date: string, end_date: string) => {
    const response = await apiClient.get('/api/v1/export/reports/accuracy/excel', {
      params: { start_date, end_date },
      responseType: 'blob',
    });
    return response.data as Blob;
  },
  exportDivergenceReportExcel: async (start_date: string, end_date: string) => {
    const response = await apiClient.get('/api/v1/export/reports/divergences/excel', {
      params: { start_date, end_date },
      responseType: 'blob',
    });
    return response.data as Blob;
  },
};

const getFilenameSuffix = () => new Date().toISOString().split('T')[0];

const getErrorMessage = (error: any, fallback: string) => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim().length > 0) {
    return detail;
  }
  return fallback;
};

export function useExportSalesExcel() {
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: (params?: { start_date?: string; end_date?: string }) =>
      exportApi.exportSalesExcel(params),
    onSuccess: (blob) => {
      saveAs(blob, `vendas_${getFilenameSuffix()}.xlsx`);
      showNotification('Vendas exportadas em Excel com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(getErrorMessage(error, 'Erro ao exportar vendas'), 'error');
    },
  });
}

export function useExportAccuracyReportExcel() {
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: ({ start_date, end_date }: { start_date: string; end_date: string }) =>
      exportApi.exportAccuracyReportExcel(start_date, end_date),
    onSuccess: (blob) => {
      saveAs(blob, `relatorio_accuracy_${getFilenameSuffix()}.xlsx`);
      showNotification('Relatório de accuracy exportado com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(getErrorMessage(error, 'Erro ao exportar relatório de accuracy'), 'error');
    },
  });
}

export function useExportDivergenceReportExcel() {
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: ({ start_date, end_date }: { start_date: string; end_date: string }) =>
      exportApi.exportDivergenceReportExcel(start_date, end_date),
    onSuccess: (blob) => {
      saveAs(blob, `relatorio_divergencias_${getFilenameSuffix()}.xlsx`);
      showNotification('Relatório de divergências exportado com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(getErrorMessage(error, 'Erro ao exportar relatório de divergências'), 'error');
    },
  });
}
