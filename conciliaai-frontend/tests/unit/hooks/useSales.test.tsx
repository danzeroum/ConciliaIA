import React from 'react';
import { describe, expect, it, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSales } from '@/hooks/useSales';
import type { Sale } from '@/types/api.types';

let mockSale: Sale;

vi.mock('@/hooks/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
  }),
}));

const getSalesMock = vi.fn();
const createSaleMock = vi.fn();
const updateSaleMock = vi.fn();
const deleteSaleMock = vi.fn();
const importSalesMock = vi.fn();
const exportSalesMock = vi.fn();

vi.mock('@/api/sales.api', () => ({
  salesApi: {
    getSales: (...args: unknown[]) => getSalesMock(...args),
    getSaleById: vi.fn(() => Promise.resolve(mockSale)),
    createSale: (...args: unknown[]) => createSaleMock(...args),
    updateSale: (...args: unknown[]) => updateSaleMock(...args),
    deleteSale: (...args: unknown[]) => deleteSaleMock(...args),
    importSales: (...args: unknown[]) => importSalesMock(...args),
    exportSales: (...args: unknown[]) => exportSalesMock(...args),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useSales', () => {
  beforeEach(() => {
    mockSale = {
      id: '1',
      tenant_id: 'tenant',
      nsu: 'NSU123',
      amount: '100.00',
      date: '2024-01-01',
      payment_method: 'credit_card',
      status: 'matched',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    getSalesMock.mockResolvedValue({
      results: [mockSale],
      total: 1,
      page: 1,
      page_size: 50,
      total_pages: 1,
    });
    createSaleMock.mockResolvedValue(mockSale);
    updateSaleMock.mockResolvedValue(mockSale);
    deleteSaleMock.mockResolvedValue(undefined);
    importSalesMock.mockResolvedValue({ imported: 1, errors: 0 });
    exportSalesMock.mockResolvedValue(new Blob());
  });

  it('fetches sales data', async () => {
    const { result } = renderHook(() => useSales(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.sales).toHaveLength(1);
    expect(getSalesMock).toHaveBeenCalled();
  });

  it('creates a sale', async () => {
    const { result } = renderHook(() => useSales(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      result.current.createSale({
        nsu: 'NSU999',
        amount: '50.00',
        date: '2024-01-02',
        payment_method: 'pix',
      });
    });

    await waitFor(() => expect(createSaleMock).toHaveBeenCalled());
  });

  it('deletes a sale', async () => {
    const { result } = renderHook(() => useSales(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      result.current.deleteSale('1');
    });

    await waitFor(() => expect(deleteSaleMock).toHaveBeenCalledWith('1'));
  });
});
