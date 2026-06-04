import { useCallback, useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { reconciliationApi, ReconciliationJobStatus } from '@/api/reconciliation.api';
import { useUIStore } from '@/store/ui.store';

/**
 * Drives the asynchronous reconciliation flow: launches a job (202 + job_id)
 * and polls its status until it reaches a terminal state, surfacing progress
 * and the final result to the UI.
 */
export function useReconciliationJob() {
  const showNotification = useUIStore((state) => state.showNotification);
  const queryClient = useQueryClient();

  const [job, setJob] = useState<ReconciliationJobStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => stopPolling, [stopPolling]);

  const start = useCallback(
    async (startDate: string, endDate: string) => {
      stopPolling();
      setIsRunning(true);
      try {
        const accepted = await reconciliationApi.createJob(startDate, endDate);
        pollRef.current = setInterval(async () => {
          try {
            const status = await reconciliationApi.getStatus(accepted.job_id);
            setJob(status);
            if (status.status === 'completed' || status.status === 'failed') {
              stopPolling();
              setIsRunning(false);
              if (status.status === 'completed') {
                showNotification(
                  `Reconciliação concluída: ${status.result?.matched ?? 0} matches, ` +
                    `${status.result?.divergences ?? 0} divergências.`,
                  'success'
                );
                queryClient.invalidateQueries({ queryKey: ['divergences'] });
                queryClient.invalidateQueries({ queryKey: ['stats'] });
                queryClient.invalidateQueries({ queryKey: ['sales'] });
              } else {
                showNotification(status.error || 'Falha na reconciliação', 'error');
              }
            }
          } catch (err: any) {
            stopPolling();
            setIsRunning(false);
            showNotification(
              err.response?.data?.detail || 'Erro ao consultar o status da reconciliação',
              'error'
            );
          }
        }, 1500);
      } catch (err: any) {
        setIsRunning(false);
        showNotification(
          err.response?.data?.detail || 'Erro ao iniciar a reconciliação',
          'error'
        );
      }
    },
    [queryClient, showNotification, stopPolling]
  );

  return { start, job, isRunning };
}
