import type { ReactNode } from 'react';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useExportSalesExcel, exportApi } from '../useExport';

const showNotificationMock = vi.fn();
const saveAsMock = vi.fn();

vi.mock('file-saver', () => ({
  saveAs: (...args: unknown[]) => saveAsMock(...args),
}));

vi.mock('@/store/ui.store', () => ({
  useUIStore: (selector: (state: { showNotification: typeof showNotificationMock }) => unknown) =>
    selector({ showNotification: showNotificationMock }),
}));

const createWrapper = () => {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  }

  return Wrapper;
};

describe('useExportSalesExcel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('downloads Excel file successfully', async () => {
    const blob = new Blob(['test']);
    const exportSpy = vi.spyOn(exportApi, 'exportSalesExcel').mockResolvedValue(blob);

    const { result } = renderHook(() => useExportSalesExcel(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ start_date: '2024-01-01', end_date: '2024-01-31' });
    });

    expect(exportSpy).toHaveBeenCalledWith({ start_date: '2024-01-01', end_date: '2024-01-31' });
    expect(saveAsMock).toHaveBeenCalled();
    expect(showNotificationMock).toHaveBeenCalledWith(
      'Vendas exportadas em Excel com sucesso',
      'success'
    );
  });

  it('handles export errors', async () => {
    const exportSpy = vi
      .spyOn(exportApi, 'exportSalesExcel')
      .mockRejectedValue(new Error('failed'));

    const { result } = renderHook(() => useExportSalesExcel(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await expect(result.current.mutateAsync({})).rejects.toThrowError();
    });

    expect(exportSpy).toHaveBeenCalled();
    expect(showNotificationMock).toHaveBeenCalledWith('Erro ao exportar vendas', 'error');
  });
});
