import type { ReactNode } from 'react';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useSales, useCreateSale, useUpdateSale, useDeleteSale } from '../useSales';
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

type WrapperProps = {
  children: ReactNode;
};

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

const mockSales = {
  items: [
    {
      id: '1',
      tenant_id: 'tenant-1',
      nsu: 'TEST001',
      amount: 100.5,
      sale_date: '2024-01-20',
      payment_method: 'credit',
      installments: 1,
      card_brand: 'Visa',
      authorization_code: 'AUTH123',
      pos_terminal_id: 'POS001',
      merchant_id: 'MERCHANT001',
      matched: false,
      match_id: null,
      customer_document: null,
      metadata: {},
      created_at: '2024-01-20T10:00:00Z',
      updated_at: '2024-01-20T10:00:00Z',
    },
  ],
  total: 1,
  page: 1,
  page_size: 50,
  total_pages: 1,
};

describe('useSales hook', () => {
  const mockedSalesApi = vi.mocked(salesApi);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches sales data successfully', async () => {
    mockedSalesApi.list.mockResolvedValue(mockSales);

    const { result } = renderHook(() => useSales(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockSales);
    expect(mockedSalesApi.list).toHaveBeenCalledWith(undefined);
  });

  it('creates a sale', async () => {
    const newSaleData = {
      nsu: 'NEW001',
      amount: 200,
      sale_date: '2024-01-21',
      payment_method: 'debit',
      installments: 1,
    };

    mockedSalesApi.create.mockResolvedValue({
      ...mockSales.items[0],
      ...newSaleData,
      id: '2',
    });

    const { result } = renderHook(() => useCreateSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync(newSaleData);
    });

    expect(mockedSalesApi.create).toHaveBeenCalledWith(newSaleData);
  });

  it('updates a sale', async () => {
    const updateData = { amount: 150 };

    mockedSalesApi.update.mockResolvedValue({
      ...mockSales.items[0],
      ...updateData,
    });

    const { result } = renderHook(() => useUpdateSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ id: '1', data: updateData });
    });

    expect(mockedSalesApi.update).toHaveBeenCalledWith('1', updateData);
  });

  it('deletes a sale', async () => {
    mockedSalesApi.delete.mockResolvedValue(undefined);

    const { result } = renderHook(() => useDeleteSale(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync('1');
    });

    expect(mockedSalesApi.delete).toHaveBeenCalledWith('1');
  });

  it('handles API errors', async () => {
    mockedSalesApi.list.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useSales(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });
});
