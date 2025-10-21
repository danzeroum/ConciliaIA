import type { ReactNode } from 'react';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useTransactions, useImportTransactions } from '@/hooks/useTransactions';
import { transactionsApi } from '@/api/transactions.api';

vi.mock('@/api/transactions.api', () => ({
  transactionsApi: {
    list: vi.fn(),
    getById: vi.fn(),
    create: vi.fn(),
    delete: vi.fn(),
    importCSV: vi.fn(),
    exportCSV: vi.fn(),
  },
}));

const showNotificationMock = vi.fn();
vi.mock('@/store/ui.store', () => ({
  useUIStore: (selector: (state: { showNotification: typeof showNotificationMock }) => unknown) =>
    selector({ showNotification: showNotificationMock }),
}));

type WrapperProps = { children: ReactNode };

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: WrapperProps) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useTransactions hook integration', () => {
  const mockedTransactionsApi = vi.mocked(transactionsApi);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('retrieves the transactions list', async () => {
    const mockResponse = {
      items: [
        {
          id: '1',
          tenant_id: 'tenant-1',
          nsu: 'TX123',
          acquirer: 'cielo',
          amount: 100,
          transaction_date: '2024-01-01',
          settlement_date: '2024-01-02',
          card_brand: 'Visa',
          authorization_code: null,
          mdr_rate: null,
          mdr_amount: null,
          installments: 1,
          terminal_id: null,
          merchant_id: null,
          matched: true,
          match_id: 'match-1',
          metadata: {},
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      page_size: 50,
      total_pages: 1,
    };

    mockedTransactionsApi.list.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useTransactions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResponse);
    expect(mockedTransactionsApi.list).toHaveBeenCalledWith(undefined);
  });

  it('imports transactions from CSV', async () => {
    const importResult = { imported: 10, failed: 0 };
    mockedTransactionsApi.importCSV.mockResolvedValue(importResult);

    const { result } = renderHook(() => useImportTransactions(), {
      wrapper: createWrapper(),
    });

    const file = new File(['content'], 'transactions.csv', { type: 'text/csv' });

    await act(async () => {
      await result.current.mutateAsync(file);
    });

    expect(mockedTransactionsApi.importCSV).toHaveBeenCalledWith(file);
  });
});
