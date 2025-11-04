import type { ReactNode } from 'react';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useSales, useCreateSale, useDeleteSale, useUpdateSale } from '@/hooks/useSales';
import { salesApi } from '@/api/sales.api';

vi.mock('@/api/sales.api', () => ({
  salesApi: {
    list: vi.fn(),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
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

describe('useSales hook integration', () => {
  const mockedSalesApi = vi.mocked(salesApi);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns sales list data', async () => {
    const mockResponse = {
      items: [
        {
          id: '1',
          tenant_id: 'tenant-1',
          nsu: 'NSU123',
          amount: 100,
          sale_date: '2024-01-01',
          payment_method: 'credit',
          installments: 1,
          card_brand: 'Visa',
          authorization_code: null,
          pos_terminal_id: null,
          merchant_id: null,
          matched: true,
          match_id: 'match-1',
          customer_document: null,
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

    mockedSalesApi.list.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSales(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResponse);
    expect(mockedSalesApi.list).toHaveBeenCalledWith(undefined);
  });

  it('creates a sale via mutation', async () => {
    const newSale = {
      nsu: 'NSU999',
      amount: 50,
      sale_date: '2024-01-02',
      payment_method: 'pix',
      installments: 1,
    };

    mockedSalesApi.create.mockResolvedValue({
      ...newSale,
      id: '2',
      tenant_id: 'tenant-1',
      matched: false,
      card_brand: null,
      authorization_code: null,
      pos_terminal_id: null,
      merchant_id: null,
      match_id: null,
      customer_document: null,
      metadata: {},
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    });

    const { result } = renderHook(() => useCreateSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync(newSale);
    });

    expect(mockedSalesApi.create).toHaveBeenCalledWith(newSale);
  });

  it('updates a sale', async () => {
    const updateData = { amount: 150 };
    mockedSalesApi.update.mockResolvedValue({ id: '1', ...updateData });

    const { result } = renderHook(() => useUpdateSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ id: '1', data: updateData });
    });

    expect(mockedSalesApi.update).toHaveBeenCalledWith('1', updateData);
  });

  it('deletes a sale via mutation', async () => {
    mockedSalesApi.delete.mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync('1');
    });

    expect(mockedSalesApi.delete).toHaveBeenCalledWith('1');
  });
});
