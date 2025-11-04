import { apiClient } from './axios-config';

export interface KPIMetrics {
  accuracy: number;
  total_matches: number;
  pending_divergences: number;
  resolved_today: number;
  total_sales: number;
  total_transactions: number;
  total_amount_reconciled: number;
}

export interface TrendDataPoint {
  date: string;
  value: number;
}

export interface DashboardStatsResponse {
  kpis: KPIMetrics;
  accuracy_trend: TrendDataPoint[];
  top_divergence_types: Array<{ type: string; count: number }>;
  acquirer_breakdown: Array<{ acquirer: string; transactions: number; amount: number }>;
}

export const statsApi = {
  // Get dashboard statistics
  getDashboard: async (days: number = 30): Promise<DashboardStatsResponse> => {
    const response = await apiClient.get('/api/v1/stats/dashboard', {
      params: { days },
    });
    return response.data;
  },

  // Get KPIs only
  getKPIs: async (days: number = 30): Promise<KPIMetrics> => {
    const response = await apiClient.get('/api/v1/stats/kpis', {
      params: { days },
    });
    return response.data;
  },
};
