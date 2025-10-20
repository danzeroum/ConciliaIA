import type { Sale } from '@/types/api.types';
import { SaleModal } from './SaleModal';

interface EditSaleModalProps {
  open: boolean;
  sale: Sale | null;
  onClose: () => void;
}

export function EditSaleModal({ open, sale, onClose }: EditSaleModalProps) {
  return <SaleModal open={open} onClose={onClose} mode="edit" sale={sale} />;
}
