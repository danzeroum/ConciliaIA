import { apiClient } from './axios-config';

export interface ReconciliationJobAccepted {
  job_id: string;
  status: string;
}

export interface ReconciliationJobResult {
  matched: number;
  divergences: number;
  accuracy: number;
  precision: number;
  recall: number;
}

export interface ReconciliationJobStatus {
  job_id: string;
  tenant_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_date: string | null;
  end_date: string | null;
  checkpoints: Record<string, unknown>;
  result: ReconciliationJobResult | null;
  error: string | null;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
}

export interface ProcessMetrics {
  completed_jobs: number;
  failed_jobs: number;
  pending_jobs: number;
  duration_p50_seconds: number | null;
  duration_p95_seconds: number | null;
  matches_last_30d: number;
  divergence_backlog: number;
  auto_approval_rate: number | null;
}

export const reconciliationApi = {
  // Launch an asynchronous reconciliation (returns 202 + job_id)
  createJob: async (startDate: string, endDate: string): Promise<ReconciliationJobAccepted> => {
    const response = await apiClient.post('/api/v1/reconciliation-jobs', {
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },

  // Poll a job's status
  getStatus: async (jobId: string): Promise<ReconciliationJobStatus> => {
    const response = await apiClient.get(`/api/v1/reconciliation-jobs/${jobId}/status`);
    return response.data;
  },

  // Recent jobs
  list: async (limit = 20): Promise<ReconciliationJobStatus[]> => {
    const response = await apiClient.get('/api/v1/reconciliation-jobs', { params: { limit } });
    return response.data;
  },

  // Process metrics
  metrics: async (): Promise<ProcessMetrics> => {
    const response = await apiClient.get('/api/v1/reconciliation-jobs/metrics');
    return response.data;
  },
};
