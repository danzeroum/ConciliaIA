import { apiClient } from './axios-config';

export interface Divergence {
  id: string;
  tenant_id: string;
  type: string;
  sale_id: string | null;
  transaction_id: string | null;
  severity: 'critical' | 'high' | 'medium' | 'low';
  amount_at_risk: number;
  variance_percent: number | null;
  detected_at: string;
  resolved_at: string | null;
  resolution: string | null;
  notified: boolean;
  metadata: Record<string, any>;
}

export interface DivergencesListResponse {
  items: Divergence[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ResolveDivergenceRequest {
  resolution: string;
  notes?: string;
}

export const divergencesApi = {
  // List divergences
  list: async (params?: {
    type?: string;
    severity?: string;
    status?: 'open' | 'resolved' | 'ignored';
    page?: number;
    page_size?: number;
  }): Promise<DivergencesListResponse> => {
    const response = await apiClient.get('/api/v1/divergences', { params });
    return response.data;
  },

  // Get divergence by ID
  getById: async (id: string): Promise<Divergence> => {
    const response = await apiClient.get(`/api/v1/divergences/${id}`);
    return response.data;
  },

  // Resolve divergence
  resolve: async (id: string, data: ResolveDivergenceRequest): Promise<Divergence> => {
    const response = await apiClient.patch(`/api/v1/divergences/${id}/resolve`, data);
    return response.data;
  },
};
