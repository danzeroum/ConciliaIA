import React from 'react';
import { describe, expect, it, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTransactions } from '@/hooks/useTransactions';
import type { Transaction } from '@/types/api.types';

let mockTransaction: Transaction;

vi.mock('@/hooks/useNotifications', () => ({
  useNotifications: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
    showInfo: vi.fn(),
  }),
}));

const getTransactionsMock = vi.fn();
const importTransactionsMock = vi.fn();

vi.mock('@/api/transactions.api', () => ({
  transactionsApi: {
    getTransactions: (...args: unknown[]) => getTransactionsMock(...args),
    getTransactionById: vi.fn(() => Promise.resolve(mockTransaction)),
    importFromAcquirer: (...args: unknown[]) => importTransactionsMock(...args),
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

describe('useTransactions', () => {
  beforeEach(() => {
    mockTransaction = {
      id: '1',
      tenant_id: 'tenant',
      acquirer: 'cielo',
      nsu: 'TX123',
      amount: '100.00',
      transaction_date: '2024-01-01T00:00:00Z',
      card_brand: 'Visa',
      card_last_4: '1234',
      mdr_rate: '0.03',
      mdr_amount: '3.00',
      net_amount: '97.00',
      status: 'processed',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    getTransactionsMock.mockResolvedValue({
      results: [mockTransaction],
      total: 1,
      page: 1,
      page_size: 50,
      total_pages: 1,
    });
    importTransactionsMock.mockResolvedValue({ imported: 1, errors: 0 });
  });

  it('fetches transactions data', async () => {
    const { result } = renderHook(() => useTransactions(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.transactions).toHaveLength(1);
    expect(getTransactionsMock).toHaveBeenCalled();
  });

  it('imports transactions', async () => {
    const { result } = renderHook(() => useTransactions(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      result.current.importFromAcquirer({ acquirer: 'cielo', startDate: '2024-01-01', endDate: '2024-01-31' });
    });

    await waitFor(() =>
      expect(importTransactionsMock).toHaveBeenCalledWith('cielo', '2024-01-01', '2024-01-31')
    );
  });
});
