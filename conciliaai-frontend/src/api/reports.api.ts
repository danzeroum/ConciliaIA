import { apiClient } from './axios-config';

export interface AccuracyDataPoint {
  date: string;
  accuracy: number;
  matches: number;
  total_sales: number;
}

export interface AccuracyReportResponse {
  period_start: string;
  period_end: string;
  overall_accuracy: number;
  total_sales: number;
  total_matches: number;
  total_divergences: number;
  trend: AccuracyDataPoint[];
}

export interface DivergenceByType {
  type: string;
  count: number;
  total_amount: number;
  percentage: number;
}

export interface DivergenceBySeverity {
  severity: string;
  count: number;
  total_amount: number;
}

export interface DivergenceAnalysisResponse {
  period_start: string;
  period_end: string;
  total_divergences: number;
  total_amount_at_risk: number;
  by_type: DivergenceByType[];
  by_severity: DivergenceBySeverity[];
  resolution_rate: number;
  avg_resolution_time_hours: number | null;
}

export interface AcquirerPerformance {
  acquirer: string;
  total_transactions: number;
  total_amount: number;
  matched_count: number;
  match_rate: number;
  avg_mdr_rate: number | null;
  total_mdr_amount: number;
}

export interface AcquirerPerformanceResponse {
  period_start: string;
  period_end: string;
  acquirers: AcquirerPerformance[];
}

export const reportsApi = {
  // Get accuracy report
  getAccuracy: async (
    start_date: string,
    end_date: string
  ): Promise<AccuracyReportResponse> => {
    const response = await apiClient.get('/api/v1/reports/accuracy', {
      params: { start_date, end_date },
    });
    return response.data;
  },

  // Get divergence analysis
  getDivergenceAnalysis: async (
    start_date: string,
    end_date: string
  ): Promise<DivergenceAnalysisResponse> => {
    const response = await apiClient.get('/api/v1/reports/divergence-analysis', {
      params: { start_date, end_date },
    });
    return response.data;
  },

  // Get acquirer performance
  getAcquirerPerformance: async (
    start_date: string,
    end_date: string
  ): Promise<AcquirerPerformanceResponse> => {
    const response = await apiClient.get('/api/v1/reports/acquirer-performance', {
      params: { start_date, end_date },
    });
    return response.data;
  },
};
