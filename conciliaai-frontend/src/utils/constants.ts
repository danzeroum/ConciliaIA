import type { Acquirer } from '@/types/api.types';
import { PaymentMethod } from '@/types/api.types';

export const PAYMENT_METHODS: ReadonlyArray<{ value: PaymentMethod; label: string }> = [
  { value: PaymentMethod.CREDIT, label: 'Crédito' },
  { value: PaymentMethod.DEBIT, label: 'Débito' },
  { value: PaymentMethod.PIX, label: 'PIX' },
  { value: PaymentMethod.VOUCHER, label: 'Voucher' },
];

export const MATCH_STATUS_OPTIONS: ReadonlyArray<{
  value: '' | 'true' | 'false';
  label: string;
}> = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Conciliados' },
  { value: 'false', label: 'Não conciliados' },
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
