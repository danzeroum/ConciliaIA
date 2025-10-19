"""Rede SOAP client for legacy webservice."""

from __future__ import annotations

from datetime import date
from typing import Dict, List
from xml.etree import ElementTree as ET

import httpx
import structlog

logger = structlog.get_logger(__name__)


class RedeSoapClient:
    """Client for Rede SOAP webservice."""

    SOAP_NAMESPACE = {
        "soap": "http://schemas.xmlsoap.org/soap/envelope/",
        "rede": "http://tempuri.org/",
    }

    def __init__(self, endpoint: str, filiacao: str, username: str, password: str) -> None:
        self.endpoint = endpoint
        self.filiacao = filiacao
        self.username = username
        self.password = password
        self.logger = logger.bind(client="RedeSoapClient", filiacao=filiacao)

    async def fetch_transactions(self, start_date: date, end_date: date) -> List[Dict]:
        soap_request = self._build_soap_request(start_date, end_date)
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info(
                    "soap_request_started",
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                )
                response = await client.post(
                    self.endpoint,
                    content=soap_request,
                    headers={
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": '"http://tempuri.org/ConsultarTransacoes"',
                    },
                )
                response.raise_for_status()
                transactions = self._parse_soap_response(response.text)
                self.logger.info(
                    "soap_request_completed", transactions_count=len(transactions)
                )
                return transactions
            except httpx.HTTPError as exc:
                self.logger.error("soap_request_failed", error=str(exc))
                raise

    def _build_soap_request(self, start_date: date, end_date: date) -> str:
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:rede="http://tempuri.org/">
  <soap:Body>
    <rede:ConsultarTransacoes>
      <rede:Filiacao>{self.filiacao}</rede:Filiacao>
      <rede:Usuario>{self.username}</rede:Usuario>
      <rede:Senha>{self.password}</rede:Senha>
      <rede:DataInicio>{start_date.strftime('%Y-%m-%d')}</rede:DataInicio>
      <rede:DataFim>{end_date.strftime('%Y-%m-%d')}</rede:DataFim>
    </rede:ConsultarTransacoes>
  </soap:Body>
</soap:Envelope>"""

    def _parse_soap_response(self, xml_response: str) -> List[Dict]:
        root = ET.fromstring(xml_response)
        body = root.find(".//soap:Body", self.SOAP_NAMESPACE)
        if body is None:
            raise ValueError("Invalid SOAP response: no Body element")

        response = body.find(
            ".//rede:ConsultarTransacoesResponse", self.SOAP_NAMESPACE
        )
        if response is None:
            raise ValueError("Invalid SOAP response: no ConsultarTransacoesResponse")

        result = response.find(
            ".//rede:ConsultarTransacoesResult", self.SOAP_NAMESPACE
        )
        if result is None:
            return []

        transactions: List[Dict] = []
        for transaction_elem in result.findall(
            ".//rede:Transacao", self.SOAP_NAMESPACE
        ):
            transaction = {
                "nsu": transaction_elem.findtext(
                    ".//rede:NSU", "", self.SOAP_NAMESPACE
                ),
                "authorization_code": transaction_elem.findtext(
                    ".//rede:CodigoAutorizacao", "", self.SOAP_NAMESPACE
                ),
                "amount": transaction_elem.findtext(
                    ".//rede:Valor", "0", self.SOAP_NAMESPACE
                ),
                "transaction_date": transaction_elem.findtext(
                    ".//rede:DataTransacao", "", self.SOAP_NAMESPACE
                ),
                "card_brand": transaction_elem.findtext(
                    ".//rede:Bandeira", "", self.SOAP_NAMESPACE
                ),
                "installments": transaction_elem.findtext(
                    ".//rede:Parcelas", "1", self.SOAP_NAMESPACE
                ),
            }
            transactions.append(transaction)
        return transactions


__all__ = ["RedeSoapClient"]
