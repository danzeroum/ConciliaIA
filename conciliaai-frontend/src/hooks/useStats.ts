import { useQuery } from '@tanstack/react-query';
import { statsApi } from '@/api/stats.api';

export function useDashboardStats(days: number = 30) {
  return useQuery({
    queryKey: ['stats', 'dashboard', days],
    queryFn: () => statsApi.getDashboard(days),
    refetchInterval: 60000, // Refresh every minute
  });
}

export function useKPIs(days: number = 30) {
  return useQuery({
    queryKey: ['stats', 'kpis', days],
    queryFn: () => statsApi.getKPIs(days),
    refetchInterval: 60000,
  });
}
