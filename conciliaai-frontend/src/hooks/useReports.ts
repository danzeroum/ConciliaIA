import { useQuery } from '@tanstack/react-query';
import { reportsApi } from '@/api/reports.api';

export function useAccuracyReport(start_date: string, end_date: string) {
  return useQuery({
    queryKey: ['reports', 'accuracy', start_date, end_date],
    queryFn: () => reportsApi.getAccuracy(start_date, end_date),
    enabled: !!start_date && !!end_date,
  });
}

export function useDivergenceAnalysisReport(start_date: string, end_date: string) {
  return useQuery({
    queryKey: ['reports', 'divergence-analysis', start_date, end_date],
    queryFn: () => reportsApi.getDivergenceAnalysis(start_date, end_date),
    enabled: !!start_date && !!end_date,
  });
}

export function useAcquirerPerformanceReport(start_date: string, end_date: string) {
  return useQuery({
    queryKey: ['reports', 'acquirer-performance', start_date, end_date],
    queryFn: () => reportsApi.getAcquirerPerformance(start_date, end_date),
    enabled: !!start_date && !!end_date,
  });
}
