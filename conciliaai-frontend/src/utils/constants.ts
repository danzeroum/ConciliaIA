import type { PaymentMethod, SaleStatus, Acquirer } from '@/types/api.types';

export const PAYMENT_METHODS: ReadonlyArray<{ value: PaymentMethod; label: string }> = [
  { value: 'credit_card', label: 'Cartão de Crédito' },
  { value: 'debit_card', label: 'Cartão de Débito' },
  { value: 'pix', label: 'PIX' },
  { value: 'boleto', label: 'Boleto' },
];

export const STATUS_OPTIONS: ReadonlyArray<{
  value: SaleStatus;
  label: string;
  color: 'success' | 'error' | 'warning';
}> = [
  { value: 'matched', label: 'Conciliado', color: 'success' },
  { value: 'unmatched', label: 'Não Conciliado', color: 'error' },
  { value: 'pending', label: 'Pendente', color: 'warning' },
];

export const ACQUIRERS: ReadonlyArray<{ value: Acquirer; label: string }> = [
  { value: 'cielo', label: 'Cielo' },
  { value: 'rede', label: 'Rede' },
  { value: 'stone', label: 'Stone' },
];

export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100] as const;
export const DEFAULT_PAGE_SIZE = 50;

export const DATE_FORMAT = 'dd/MM/yyyy';
export const DATETIME_FORMAT = 'dd/MM/yyyy HH:mm';
