import { SaleModal } from './SaleModal';

interface CreateSaleModalProps {
  open: boolean;
  onClose: () => void;
}

export function CreateSaleModal({ open, onClose }: CreateSaleModalProps) {
  return <SaleModal open={open} onClose={onClose} mode="create" sale={null} />;
}
