#!/usr/bin/env python3
"""BuildToValue v7.4-Platinum - GDPR Consent Manager
Gerencia consentimentos de usuários para processamento de dados
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

CONSENT_DB = Path(".buildtovalue/compliance/consent-database.json")


class ConsentManager:
    """Gerenciador de consentimentos GDPR"""

    def __init__(self):
        self.db_file = CONSENT_DB
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.consents = self._load_db()

    def _load_db(self) -> Dict:
        """Carrega banco de consentimentos"""
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"consents": []}
        return {"consents": []}

    def _save_db(self):
        """Salva banco de consentimentos"""
        with open(self.db_file, 'w') as f:
            json.dump(self.consents, f, indent=2)

    def record_consent(self, user_id: str, purposes: List[str],
                       method: str = "explicit") -> Dict:
        """Registra consentimento de usuário"""
        consent = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "purposes": purposes,
            "method": method,  # explicit, implicit, legitimate_interest
            "status": "active",
            "withdrawn_at": None,
            "ip_address": "[MASKED]",  # Substituir por IP real se necessário
            "user_agent": "[MASKED]"
        }

        self.consents["consents"].append(consent)
        self._save_db()

        print(f"✅ Consentimento registrado para {user_id}")
        return consent

    def withdraw_consent(self, user_id: str, purposes: Optional[List[str]] = None) -> bool:
        """Retira consentimento de usuário"""
        found = False

        for consent in self.consents["consents"]:
            if consent["user_id"] == user_id and consent["status"] == "active":
                if purposes is None or any(p in consent["purposes"] for p in purposes):
                    consent["status"] = "withdrawn"
                    consent["withdrawn_at"] = datetime.utcnow().isoformat() + "Z"
                    found = True

        if found:
            self._save_db()
            print(f"✅ Consentimento retirado para {user_id}")
            return True
        else:
            print(f"⚠️ Nenhum consentimento ativo encontrado para {user_id}")
            return False

    def check_consent(self, user_id: str, purpose: str) -> bool:
        """Verifica se usuário consentiu para um propósito específico"""
        for consent in self.consents["consents"]:
            if (consent["user_id"] == user_id and
                consent["status"] == "active" and
                purpose in consent["purposes"]):
                return True
        return False

    def list_user_consents(self, user_id: str) -> List[Dict]:
        """Lista todos os consentimentos de um usuário"""
        return [c for c in self.consents["consents"] if c["user_id"] == user_id]

    def generate_consent_report(self) -> str:
        """Gera relatório de consentimentos"""
        total = len(self.consents["consents"])
        active = sum(1 for c in self.consents["consents"] if c["status"] == "active")
        withdrawn = sum(1 for c in self.consents["consents"] if c["status"] == "withdrawn")

        report = []
        report.append("=" * 60)
        report.append("GDPR Consent Management Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.utcnow().isoformat()}Z")
        report.append("")
        report.append(f"Total Consents:     {total}")
        report.append(f"Active:             {active}")
        report.append(f"Withdrawn:          {withdrawn}")
        report.append("")

        # Consentimentos por propósito
        purposes = {}
        for consent in self.consents["consents"]:
            if consent["status"] == "active":
                for purpose in consent["purposes"]:
                    purposes[purpose] = purposes.get(purpose, 0) + 1

        if purposes:
            report.append("Active Consents by Purpose:")
            for purpose, count in sorted(purposes.items(), key=lambda x: -x[1]):
                report.append(f"  - {purpose}: {count}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    """CLI para gerenciamento de consentimentos"""
    import argparse

    parser = argparse.ArgumentParser(description='GDPR Consent Manager')
    subparsers = parser.add_subparsers(dest='command', help='Comando', required=True)

    # Record consent
    record_parser = subparsers.add_parser('record', help='Registrar consentimento')
    record_parser.add_argument('user_id', help='ID do usuário')
    record_parser.add_argument('purposes', nargs='+', help='Propósitos')
    record_parser.add_argument('--method', default='explicit',
                               choices=['explicit', 'implicit', 'legitimate_interest'])

    # Withdraw consent
    withdraw_parser = subparsers.add_parser('withdraw', help='Retirar consentimento')
    withdraw_parser.add_argument('user_id', help='ID do usuário')
    withdraw_parser.add_argument('--purposes', nargs='*', help='Propósitos específicos')

    # Check consent
    check_parser = subparsers.add_parser('check', help='Verificar consentimento')
    check_parser.add_argument('user_id', help='ID do usuário')
    check_parser.add_argument('purpose', help='Propósito')

    # List consents
    list_parser = subparsers.add_parser('list', help='Listar consentimentos')
    list_parser.add_argument('user_id', help='ID do usuário')

    # Report
    subparsers.add_parser('report', help='Gerar relatório')

    args = parser.parse_args()

    manager = ConsentManager()

    if args.command == 'record':
        manager.record_consent(args.user_id, args.purposes, args.method)
    elif args.command == 'withdraw':
        manager.withdraw_consent(args.user_id, args.purposes)
    elif args.command == 'check':
        has_consent = manager.check_consent(args.user_id, args.purpose)
        if has_consent:
            print(f"✅ Usuário {args.user_id} consentiu para: {args.purpose}")
            return 0
        else:
            print(f"❌ Usuário {args.user_id} NÃO consentiu para: {args.purpose}")
            return 1
    elif args.command == 'list':
        consents = manager.list_user_consents(args.user_id)
        if consents:
            print(json.dumps(consents, indent=2))
        else:
            print(f"⚠️ Nenhum consentimento encontrado para: {args.user_id}")
    elif args.command == 'report':
        print(manager.generate_consent_report())

    return 0


if __name__ == '__main__':
    sys.exit(main())
