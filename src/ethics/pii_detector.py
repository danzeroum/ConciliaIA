# src/ethics/pii_detector.py
"""
PII Detector - Detecta exposição de dados pessoais
Compliance: LGPD (Brasil) e GDPR (Europa)
"""

import re
from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PIIMatch:
    """Representa uma ocorrência de PII detectada"""
    pii_type: str
    value: str  # Mascarado para não expor o dado real
    location: str  # arquivo:linha
    severity: str  # critical, high, medium, low
    recommendation: str


class PIIDetector:
    """Detecta exposição de PII em código, logs e documentação"""
    
    def __init__(self):
        # Padrões regex para detecção de PII
        self.patterns = {
            'cpf': {
                'regex': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
                'severity': 'critical',
                'description': 'CPF (Cadastro de Pessoa Física)',
                'lgpd_category': 'Dado Pessoal Sensível'
            },
            'cnpj': {
                'regex': r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}',
                'severity': 'high',
                'description': 'CNPJ (Cadastro Nacional de Pessoa Jurídica)',
                'lgpd_category': 'Dado Corporativo'
            },
            'email': {
                'regex': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'severity': 'high',
                'description': 'Endereço de e-mail',
                'lgpd_category': 'Dado Pessoal'
            },
            'phone_br': {
                'regex': r'(?:\+55\s?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}',
                'severity': 'high',
                'description': 'Telefone brasileiro',
                'lgpd_category': 'Dado Pessoal'
            },
            'credit_card': {
                'regex': r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',
                'severity': 'critical',
                'description': 'Número de cartão de crédito',
                'lgpd_category': 'Dado Financeiro Sensível'
            },
            'ip_address': {
                'regex': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                'severity': 'medium',
                'description': 'Endereço IP',
                'lgpd_category': 'Dado de Identificação'
            },
            'rg': {
                'regex': r'\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]',
                'severity': 'critical',
                'description': 'RG (Registro Geral)',
                'lgpd_category': 'Dado Pessoal Sensível'
            },
            'password': {
                'regex': r'(?:password|senha|pwd)\s*[=:]\s*["\']?[^\s"\']{6,}',
                'severity': 'critical',
                'description': 'Credencial exposta',
                'lgpd_category': 'Dado de Autenticação'
            },
            'api_key': {
                'regex': r'(?:api[_-]?key|apikey|token)\s*[=:]\s*["\']?[a-zA-Z0-9_-]{20,}',
                'severity': 'critical',
                'description': 'API Key ou Token',
                'lgpd_category': 'Credencial de Sistema'
            },
            'jwt': {
                'regex': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
                'severity': 'critical',
                'description': 'JWT Token',
                'lgpd_category': 'Token de Autenticação'
            }
        }
        
        # Whitelist de padrões permitidos
        self.whitelist = {
            'cpf': ['000.000.000-00', '111.111.111-11'],  # CPFs de teste
            'email': ['test@example.com', 'user@test.local'],
            'phone_br': ['(00) 0000-0000', '(11) 9999-9999']
        }
        
        # Extensões de arquivos a serem escaneados
        self.scannable_extensions = {
            '.py', '.js', '.ts', '.java', '.go', '.rb',
            '.log', '.txt', '.md', '.json', '.yaml', '.yml',
            '.env', '.config', '.ini', '.properties'
        }
    
    def scan_file(self, file_path: Path) -> List[PIIMatch]:
        """Escaneia um arquivo em busca de PII"""
        matches = []
        
        # Verificar extensão
        if file_path.suffix not in self.scannable_extensions:
            return matches
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
                for line_num, line in enumerate(lines, start=1):
                    # Escanear cada padrão
                    for pii_type, config in self.patterns.items():
                        pattern = re.compile(config['regex'], re.IGNORECASE)
                        
                        for match in pattern.finditer(line):
                            value = match.group(0)
                            
                            # Verificar whitelist
                            if self._is_whitelisted(pii_type, value):
                                continue
                            
                            # Mascarar valor para não expor PII no relatório
                            masked_value = self._mask_value(value)
                            
                            matches.append(PIIMatch(
                                pii_type=pii_type,
                                value=masked_value,
                                location=f"{file_path}:{line_num}",
                                severity=config['severity'],
                                recommendation=self._get_recommendation(pii_type, file_path)
                            ))
        
        except Exception as e:
            print(f"⚠️  Erro ao escanear {file_path}: {e}")
        
        return matches
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[PIIMatch]:
        """Escaneia um diretório em busca de PII"""
        all_matches = []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                matches = self.scan_file(file_path)
                all_matches.extend(matches)

        return all_matches

    def scan_text(self, text: str, source: str = "inline") -> List[PIIMatch]:
        """Escaneia um texto bruto utilizando os mesmos padrões de PII."""
        matches: List[PIIMatch] = []
        lines = text.splitlines()
        if not lines and text:
            lines = [text]

        for line_num, line in enumerate(lines, start=1):
            for pii_type, config in self.patterns.items():
                pattern = re.compile(config['regex'], re.IGNORECASE)

                for match in pattern.finditer(line):
                    value = match.group(0)

                    if self._is_whitelisted(pii_type, value):
                        continue

                    masked_value = self._mask_value(value)

                    matches.append(
                        PIIMatch(
                            pii_type=pii_type,
                            value=masked_value,
                            location=f"{source}:{line_num}",
                            severity=config['severity'],
                            recommendation=self._get_recommendation(pii_type, Path(source)),
                        )
                    )

        return matches
    
    def _is_whitelisted(self, pii_type: str, value: str) -> bool:
        """Verifica se o valor está na whitelist"""
        if pii_type not in self.whitelist:
            return False
        
        return value in self.whitelist[pii_type]
    
    def _mask_value(self, value: str) -> str:
        """Mascara o valor de PII para não expor no relatório"""
        if len(value) <= 4:
            return '*' * len(value)
        
        # Manter primeiros 2 e últimos 2 caracteres
        return value[:2] + '*' * (len(value) - 4) + value[-2:]
    
    def _get_recommendation(self, pii_type: str, file_path: Path) -> str:
        """Retorna recomendação baseada no tipo de PII e localização"""
        recommendations = {
            'cpf': "Remover CPF ou usar mascaramento. Em logs, use apenas os 3 últimos dígitos.",
            'cnpj': "Remover CNPJ ou usar mascaramento. Para auditoria, armazene de forma criptografada.",
            'email': "Evitar expor e-mails. Use IDs ou hashes para referência.",
            'phone_br': "Mascarar telefone ou remover. Use apenas para validação interna.",
            'credit_card': "CRÍTICO: Nunca armazenar número de cartão completo. Use tokenização PCI-DSS.",
            'password': "CRÍTICO: Nunca logar senhas. Use apenas hashes seguros (bcrypt/argon2).",
            'api_key': "CRÍTICO: Mover para variáveis de ambiente ou secret manager.",
            'jwt': "Não logar tokens JWT. Use apenas para autenticação em requests."
        }
        
        base_rec = recommendations.get(pii_type, "Revisar exposição de dado pessoal.")
        
        # Adicionar recomendação específica por tipo de arquivo
        if '.log' in file_path.suffixes:
            base_rec += " Configurar log masking/sanitization."
        elif file_path.name.startswith('.env'):
            base_rec += " Adicionar ao .gitignore e usar secret manager."
        elif file_path.suffix in ['.py', '.js', '.java']:
            base_rec += " Remover do código-fonte e externalizar configuração."
        
        return base_rec
    
    def generate_report(self, matches: List[PIIMatch]) -> Dict:
        """Gera relatório consolidado de PII"""
        # Agrupar por severidade
        by_severity = {
            'critical': [m for m in matches if m.severity == 'critical'],
            'high': [m for m in matches if m.severity == 'high'],
            'medium': [m for m in matches if m.severity == 'medium'],
            'low': [m for m in matches if m.severity == 'low']
        }
        
        # Agrupar por tipo
        by_type = {}
        for match in matches:
            if match.pii_type not in by_type:
                by_type[match.pii_type] = []
            by_type[match.pii_type].append(match)
        
        # Arquivos com maior número de exposições
        by_file = {}
        for match in matches:
            file_path = match.location.split(':')[0]
            if file_path not in by_file:
                by_file[file_path] = 0
            by_file[file_path] += 1
        
        top_files = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_exposures': len(matches),
            'by_severity': {
                'critical': len(by_severity['critical']),
                'high': len(by_severity['high']),
                'medium': len(by_severity['medium']),
                'low': len(by_severity['low'])
            },
            'by_type': {pii_type: len(occurrences) for pii_type, occurrences in by_type.items()},
            'top_files': [{'file': f, 'count': c} for f, c in top_files],
            'matches': [
                {
                    'type': m.pii_type,
                    'value': m.value,
                    'location': m.location,
                    'severity': m.severity,
                    'recommendation': m.recommendation
                }
                for m in matches
            ],
            'compliance_status': 'FAIL' if len(by_severity['critical']) > 0 else 'PASS',
            'lgpd_risk_level': self._calculate_risk_level(by_severity)
        }
    
    def _calculate_risk_level(self, by_severity: Dict) -> str:
        """Calcula nível de risco LGPD baseado nas exposições"""
        if len(by_severity['critical']) > 0:
            return "ALTO - Violação grave de LGPD"
        elif len(by_severity['high']) > 5:
            return "MÉDIO - Risco significativo de violação"
        elif len(by_severity['high']) > 0 or len(by_severity['medium']) > 10:
            return "BAIXO - Requer atenção"
        else:
            return "MÍNIMO - Conformidade adequada"


# CLI para uso standalone
if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description='PII Detector - LGPD Compliance Scanner')
    parser.add_argument('path', type=str, nargs='?', default='.', help='Arquivo ou diretório para escanear')
    parser.add_argument('--recursive', action='store_true', help='Escanear recursivamente')
    parser.add_argument('--output', type=str, help='Arquivo de saída JSON')
    parser.add_argument('--fail-on-critical', action='store_true', help='Exit code 1 se encontrar PII crítico')
    
    args = parser.parse_args()
    
    detector = PIIDetector()
    path = Path(args.path)
    
    print(f"🔍 Escaneando {path} em busca de PII...")
    
    if path.is_file():
        matches = detector.scan_file(path)
    elif path.is_dir():
        matches = detector.scan_directory(path, recursive=args.recursive or True)
    else:
        print(f"❌ Caminho inválido: {path}")
        exit(1)
    
    report = detector.generate_report(matches)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ Relatório salvo em {args.output}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  PII DETECTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Exposures: {report['total_exposures']}")
    print(f"Critical: {report['by_severity']['critical']} | High: {report['by_severity']['high']}")
    print(f"Medium: {report['by_severity']['medium']} | Low: {report['by_severity']['low']}")
    print(f"LGPD Risk: {report['lgpd_risk_level']}")
    print(f"Status: {report['compliance_status']}")
    print(f"{'='*60}\n")
    
    # Exit code
    if args.fail_on_critical and report['by_severity']['critical'] > 0:
        exit(1)
