import { type ReactNode, useCallback, useMemo, useRef, useState } from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import type { SxProps, Theme } from '@mui/material/styles';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import { useUIStore } from '@/store/ui.store';

interface PDFExportProps {
  targetElementId?: string;
  filename?: string;
  buttonLabel?: string;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'inherit' | 'primary' | 'secondary';
  onExport?: () => void;
  sx?: SxProps<Theme>;
  children?: ReactNode;
}

export function PDFExport({
  targetElementId,
  filename = 'documento',
  buttonLabel = 'PDF',
  variant = 'outlined',
  color = 'primary',
  onExport,
  sx,
  children,
}: PDFExportProps) {
  const [isExporting, setIsExporting] = useState(false);
  const showNotification = useUIStore((state) => state.showNotification);
  const fallbackRef = useRef<HTMLDivElement>(null);

  const resolveTarget = useCallback((): HTMLElement | null => {
    if (targetElementId) {
      return document.getElementById(targetElementId);
    }
    return fallbackRef.current;
  }, [targetElementId]);

  const exportToPDF = useCallback(async () => {
    const target = resolveTarget();

    if (!target) {
      showNotification('Elemento para exportação não encontrado', 'error');
      return;
    }

    try {
      setIsExporting(true);
      const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
        import('jspdf'),
        import('html2canvas'),
      ]);

      const canvas = await html2canvas(target, {
        backgroundColor: '#ffffff',
        scale: 2,
        useCORS: true,
        logging: false,
        windowWidth: target.scrollWidth,
        windowHeight: target.scrollHeight,
      });

      const imageData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = 210;
      const pageHeight = 297;
      const imageWidth = pageWidth;
      const imageHeight = (canvas.height * imageWidth) / canvas.width;

      pdf.addImage(imageData, 'PNG', 0, 0, imageWidth, imageHeight);

      let heightLeft = imageHeight - pageHeight;
      let position = 0;

      while (heightLeft > 0) {
        position -= pageHeight;
        pdf.addPage();
        pdf.addImage(imageData, 'PNG', 0, position, imageWidth, imageHeight);
        heightLeft -= pageHeight;
      }

      const timestamp = new Date().toISOString().split('T')[0];
      pdf.save(`${filename}_${timestamp}.pdf`);

      showNotification('PDF exportado com sucesso', 'success');
      onExport?.();
    } catch (error) {
      console.error('Erro ao exportar PDF', error);
      showNotification('Erro ao exportar PDF', 'error');
    } finally {
      setIsExporting(false);
    }
  }, [filename, onExport, resolveTarget, showNotification]);

  const buttonContent = useMemo(
    () => (
      <Button
        variant={variant}
        color={color}
        startIcon={isExporting ? <CircularProgress size={20} /> : <PictureAsPdfIcon />}
        onClick={exportToPDF}
        disabled={isExporting}
      >
        {isExporting ? 'Exportando...' : buttonLabel}
      </Button>
    ),
    [buttonLabel, color, exportToPDF, isExporting, variant]
  );

  const containerSx = useMemo<SxProps<Theme>>(() => {
    if (!sx) {
      return { display: 'inline-flex' };
    }

    if (Array.isArray(sx)) {
      return [{ display: 'inline-flex' }, ...sx];
    }

    if (typeof sx === 'function') {
      return [(theme: Theme) => ({ display: 'inline-flex', ...sx(theme) })];
    }

    return { display: 'inline-flex', ...sx };
  }, [sx]);

  return (
    <Box component="span" sx={containerSx}>
      {buttonContent}
      <Box
        ref={fallbackRef}
        sx={{ display: targetElementId ? 'none' : 'block', position: 'absolute', left: -9999 }}
      >
        {children}
      </Box>
    </Box>
  );
}
