import {
  buildParcelamentoBreakdown,
  evaluateICPlus,
  getRequestCategory,
  getRequestReasonsSummary,
  getStatusSummary,
  isChargeback,
  validateAdjustmentCode,
  validateAutenticacao,
  validateParcelamento,
  validateRequestRecord,
  validateStatus,
} from '../../../../src/integrations/acquirers/rede/rede-transaction-validator';
import {
  RedeRegistro005Request,
  RedeRegistro008,
  RedeRegistro012,
  RedeRegistro033,
} from '../../../../src/integrations/acquirers/rede/rede-eevc-parser';

describe('Rede transaction validator', () => {
  it('flags chargeback codes using reference tables', () => {
    expect(isChargeback('3001')).toBe(true);
    expect(isChargeback('0017')).toBe(false);
  });

  it('validates status severity', () => {
    const registro = {
      tipoRegistro: '008',
      numeroPV: '000123456',
      numeroRV: '000654321',
      dataCVNSU: null,
      valorCVNSU: 100,
      numeroCartao: '411111******1111',
      statusCVNSU: '10',
      numeroCVNSU: '123456789012',
      numeroAutorizacao: '654321',
      tipoCaptura: '0',
      numeroTerminal: 'TERM0001',
      bandeira: '3',
      codigoServico: '001',
    } as RedeRegistro008;

    const result = validateStatus(registro);
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('Cartão bloqueado');
  });

  it('validates parcelamento limits and totals', () => {
    const registro: RedeRegistro012 = {
      tipoRegistro: '012',
      numeroPV: '000123456',
      numeroRV: '000654321',
      dataCVNSU: null,
      valorCVNSU: 24,
      numeroCartao: '411111******1111',
      statusCVNSU: '0',
      numeroCVNSU: '654321098765',
      numeroAutorizacao: '321654',
      tipoCaptura: '1',
      numeroTerminal: 'TERM0002',
      bandeira: '1',
      codigoServico: '001',
      numeroParcelas: 3,
      valorPrimeiraParcela: 8,
      valorDemaisParcelas: 8,
    };

    expect(validateParcelamento(registro).valid).toBe(true);
    const breakdown = buildParcelamentoBreakdown(registro);
    expect(breakdown.valorTotalCalculado).toBeCloseTo(24, 4);
  });

  it('requires documentation for documentation chargebacks', () => {
    const request: RedeRegistro005Request = {
      tipoRegistro: '005',
      numeroPV: '000123456',
      dataRequest: null,
      codigoMotivo: '0017',
      valorRequest: 100,
      numeroCartao: '411111******1111',
      nsuOriginal: '123456789012',
      numeroProcesso: 'PROC12345678',
    };
    const chargeback: RedeRegistro005Request = { ...request, codigoMotivo: '3001' };

    expect(validateRequestRecord(request).valid).toBe(true);
    expect(validateRequestRecord(chargeback).valid).toBe(true);
    expect(isChargeback(chargeback.codigoMotivo)).toBe(true);
  });

  it('validates ecommerce authentication indicator', () => {
    const registro = {
      tipoRegistro: '033',
      numeroPV: '000123456',
      numeroRV: '000654321',
      dataCVNSU: null,
      valorCVNSU: 10,
      numeroCartao: '411111******1111',
      statusCVNSU: '0',
      numeroCVNSU: '987654321000',
      numeroAutorizacao: '654321',
      tipoCaptura: '1',
      numeroTerminal: 'TERM0003',
      bandeira: '3',
      codigoServico: '001',
      tid: 'TID1234567890123456',
      numeroPedido: 'PED-1000',
      indicadorAutenticacao: 'Y',
      codigoAVS: 'Y',
    } as RedeRegistro033;

    expect(validateAutenticacao(registro).valid).toBe(true);
    const invalid: RedeRegistro033 = {
      tipoRegistro: '033',
      numeroPV: registro.numeroPV,
      numeroRV: registro.numeroRV,
      dataCVNSU: registro.dataCVNSU,
      valorCVNSU: registro.valorCVNSU,
      numeroCartao: registro.numeroCartao,
      statusCVNSU: registro.statusCVNSU,
      numeroCVNSU: registro.numeroCVNSU,
      numeroAutorizacao: registro.numeroAutorizacao,
      tipoCaptura: registro.tipoCaptura,
      numeroTerminal: registro.numeroTerminal,
      bandeira: registro.bandeira,
      codigoServico: registro.codigoServico,
      tid: registro.tid,
      numeroPedido: registro.numeroPedido,
      indicadorAutenticacao: 'N',
      codigoAVS: registro.codigoAVS,
    };
    expect(validateAutenticacao(invalid).valid).toBe(false);
  });

  it('validates adjustment codes', () => {
    expect(validateAdjustmentCode('1').valid).toBe(true);
    expect(validateAdjustmentCode('999').valid).toBe(false);
  });

  it('summarises status and request reasons', () => {
    expect(getStatusSummary().length).toBeGreaterThan(0);
    expect(getRequestReasonsSummary().length).toBeGreaterThan(0);
  });

  it('evaluates IC+ totals', () => {
    const total = evaluateICPlus({
      tipoRegistro: '029',
      numeroPV: '000123456',
      numeroRV: '000654321',
      valorInterchange: 1.5,
      valorPlus: 0.5,
      mccTransacao: '5999',
      tipoCartao: 'C',
      modoEntrada: 'C',
    });
    expect(total).toBe(2);
  });

  it('returns request category from reference table', () => {
    expect(getRequestCategory('3001')).toBe('CHARGEBACK');
    expect(getRequestCategory('4005')).toBe('OPERATIONAL');
  });
});
