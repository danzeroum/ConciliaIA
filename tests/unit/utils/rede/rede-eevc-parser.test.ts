import { RedeEEVCParser, REDE_EEVC_RECORD_LENGTH } from '../../../../src/integrations/acquirers/rede/rede-eevc-parser';

function createBlankRecord(tipo: string): string[] {
  const buffer = Array(REDE_EEVC_RECORD_LENGTH).fill(' ');
  buffer.splice(0, tipo.length, ...tipo.split(''));
  return buffer;
}

function setField(buffer: string[], start: number, value: string): void {
  for (let index = 0; index < value.length; index += 1) {
    buffer[start + index] = value[index];
  }
}

function buildRegistro008Line(): string {
  const buffer = createBlankRecord('008');
  setField(buffer, 3, '000123456');
  setField(buffer, 12, '000654321');
  setField(buffer, 21, '01032024');
  setField(buffer, 37, '000000000001000');
  setField(buffer, 67, '411111******1111');
  setField(buffer, 83, '0  ');
  setField(buffer, 86, '000000123456');
  setField(buffer, 126, '123456');
  setField(buffer, 202, '0');
  setField(buffer, 218, 'TERM0001');
  setField(buffer, 229, '3');
  setField(buffer, 260, '001');
  return buffer.join('');
}

function buildRegistro012Line(): string {
  const buffer = createBlankRecord('012');
  setField(buffer, 3, '000123456');
  setField(buffer, 12, '000654321');
  setField(buffer, 21, '02032024');
  setField(buffer, 37, '000000000002400');
  setField(buffer, 67, '411111******1111');
  setField(buffer, 83, '0  ');
  setField(buffer, 86, '000000654321');
  setField(buffer, 126, '654321');
  setField(buffer, 202, '1');
  setField(buffer, 218, 'TERM0002');
  setField(buffer, 229, '1');
  setField(buffer, 260, '001');
  setField(buffer, 203, '003');
  setField(buffer, 310, '000000000000800');
  setField(buffer, 325, '000000000000800');
  return buffer.join('');
}

describe('RedeEEVCParser', () => {
  const parser = new RedeEEVCParser();

  it('parses registro 008 with validation of reference tables', () => {
    const line = buildRegistro008Line();
    const registro = parser.parseRegistro008(line);

    expect(registro.tipoRegistro).toBe('008');
    expect(registro.numeroPV).toBe('000123456');
    expect(registro.numeroRV).toBe('000654321');
    expect(registro.dataCVNSU?.toISOString()).toBe(new Date(Date.UTC(2024, 2, 1)).toISOString());
    expect(registro.valorCVNSU).toBe(10);
    expect(registro.statusCVNSU).toBe('0');
    expect(registro.codigoServico).toBe('001');
  });

  it('parses registro 012 and validates parcelas fields', () => {
    const line = buildRegistro012Line();
    const registro = parser.parseRegistro012(line);

    expect(registro.tipoRegistro).toBe('012');
    expect(registro.numeroParcelas).toBe(3);
    expect(registro.valorPrimeiraParcela).toBe(8);
    expect(registro.valorDemaisParcelas).toBe(8);
  });

  it('throws error when record length is invalid', () => {
    expect(() => parser.parse('012')).toThrow('Tamanho de registro inválido');
  });
});
