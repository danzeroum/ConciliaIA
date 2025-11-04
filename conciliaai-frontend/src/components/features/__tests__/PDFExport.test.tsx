import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PDFExport } from '../PDFExport';

const showNotificationMock = vi.fn();
const saveMock = vi.fn();
const addImageMock = vi.fn();
const addPageMock = vi.fn();

vi.mock('@/store/ui.store', () => ({
  useUIStore: (selector: (state: { showNotification: typeof showNotificationMock }) => unknown) =>
    selector({ showNotification: showNotificationMock }),
}));

vi.mock('jspdf', () => ({
  default: vi.fn().mockImplementation(() => ({
    addImage: addImageMock,
    addPage: addPageMock,
    save: saveMock,
  })),
}));

const toDataURLMock = vi.fn().mockReturnValue('data:image/png;base64,test');

vi.mock('html2canvas', () => ({
  default: vi.fn().mockResolvedValue({
    toDataURL: toDataURLMock,
    width: 1200,
    height: 1600,
  }),
}));

describe('PDFExport', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders default button', () => {
    render(<PDFExport />);

    expect(screen.getByRole('button', { name: 'PDF' })).toBeInTheDocument();
  });

  it('exports target element to PDF successfully', async () => {
    render(
      <>
        <div id="report-content">Conteúdo do relatório</div>
        <PDFExport targetElementId="report-content" filename="relatorio" />
      </>
    );

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    });

    await waitFor(() => {
      expect(showNotificationMock).toHaveBeenCalledWith('PDF exportado com sucesso', 'success');
    });

    expect(saveMock).toHaveBeenCalled();
    expect(saveMock.mock.calls[0][0]).toMatch(/^relatorio_\d{4}-\d{2}-\d{2}\.pdf$/);
    expect(addImageMock).toHaveBeenCalled();
  });

  it('notifies error when export fails', async () => {
    const html2canvas = await import('html2canvas');
    vi.mocked(html2canvas.default).mockRejectedValueOnce(new Error('fail'));

    render(<PDFExport targetElementId="missing" />);

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'PDF' }));
    });

    await waitFor(() => {
      expect(showNotificationMock).toHaveBeenCalledWith('Elemento para exportação não encontrado', 'error');
    });
  });
});
