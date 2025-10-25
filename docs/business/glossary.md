# 📖 Glossário ConciliaAI - Termos de Negócio

## A

**Adquirente**  
Empresa que processa transações de cartão (Cielo, Rede, Stone). Cobra taxa (MDR) e repassa valor líquido ao lojista.

**Antecipação de Recebíveis**  
Receber valor de vendas parceladas antes do prazo, mediante desconto adicional.  
*Exemplo:* Receber R$ 2.850 hoje ao invés de R$ 3.000 em 30 dias (5% desconto).

**Autorização**  
Aprovação da transação pela bandeira/emissor. Não garante captura/pagamento.

## B

**Bandeira**  
Operadora da rede de cartões (Visa, Mastercard, Elo, Amex).  
*Função:* Intermediar comunicação entre adquirente e banco emissor.

**BIN (Bank Identification Number)**  
Primeiros 6 dígitos do cartão. Identifica banco emissor e bandeira.

## C

**Captura**  
Confirmação definitiva da transação após autorização.  
*Importante:* Só transações capturadas são liquidadas.

**Chargeback**  
Estorno forçado por contestação do portador. Lojista perde valor e paga tarifa (~R$ 50).  
*Prazo de contestação:* 30 dias.

**Confidence**  
Indicador 0.0-1.0 de certeza do matching. 1.00 = exact match; < 0.90 requer revisão humana.

## D

**D+N**  
Prazo de liquidação em dias úteis (D+1 débito, D+30 crédito, etc.).

**Dead Letter Queue (DLQ)**  
Fila para transações que falharam no processamento para revisão manual.

**Divergência**  
Diferença detectada entre venda (POS) e transação (adquirente).

## E

**EC (Estabelecimento Comercial)**  
Identificador do lojista na Cielo.

**EDI (Electronic Data Interchange)**  
Arquivo texto com transações enviado pela adquirente.

**Emissor**  
Banco que emitiu o cartão do portador.

## L

**Liquidação (Settlement)**  
Pagamento efetivo ao lojista. Status: pending, paid ou delayed.

## M

**Match**  
Venda reconciliada com sucesso com transação. Tipos: exact, fuzzy, installment, multiple payments.

**MDR (Merchant Discount Rate)**  
Taxa percentual cobrada pela adquirente.

## N

**NSU (Número Sequencial Único)**  
Identificador único da transação na adquirente.

## P

**Parcelado Emissor**  
Lojista recebe à vista e banco parcela para cliente.

**Parcelado Loja**  
Lojista recebe parcelado ao longo dos meses.

**POS (Point of Sale)**  
Sistema de vendas do lojista (terminal, PDV, e-commerce).

## R

**Reconciliação**  
Processo de matching vendas (POS) com transações (adquirente). Meta: >= 99.5%.

## S

**Schema Canônico**  
Formato único que normaliza dados de todas adquirentes.

**Severity**  
Classificação de urgência da divergência (critical, high, medium, low).

## T

**Taxa de Matching**
% de vendas reconciliadas com sucesso.

**TORC (Transmissão Off-line Recorrente de Crédito)**
Modalidade de captura da Rede para envio manual de arquivos CSV com vendas recorrentes.
*Exemplo:* Academia enviando parcelas mensais do plano dos alunos.

**Transaction Missing**
Venda sem transação correspondente após prazo esperado.

## V

**Valor Bruto**  
Valor total da venda ao consumidor (antes do MDR).

**Valor Líquido**  
Valor recebido após desconto do MDR.

**Variance**  
Diferença percentual entre esperado e cobrado.

---

**Versão:** 1.0  
**Atualizado:** 2025-10-18  
**Autor:** IA-Business-Analyst
