import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { divergencesApi, ResolveDivergenceRequest } from '@/api/divergences.api';
import { useUIStore } from '@/store/ui.store';

export function useDivergences(params?: {
  type?: string;
  severity?: string;
  status?: 'open' | 'resolved' | 'ignored';
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: ['divergences', params],
    queryFn: () => divergencesApi.list(params),
  });
}

export function useDivergence(id: string) {
  return useQuery({
    queryKey: ['divergences', id],
    queryFn: () => divergencesApi.getById(id),
    enabled: !!id,
  });
}

export function useResolveDivergence() {
  const queryClient = useQueryClient();
  const showNotification = useUIStore((state) => state.showNotification);

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ResolveDivergenceRequest }) =>
      divergencesApi.resolve(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['divergences'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      showNotification('Divergência resolvida com sucesso', 'success');
    },
    onError: (error: any) => {
      showNotification(
        error.response?.data?.detail || 'Erro ao resolver divergência',
        'error'
      );
    },
  });
}
