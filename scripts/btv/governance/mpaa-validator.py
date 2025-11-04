#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum - MPAA Validator
Auditoria IA-dupla com validação de integridade de prompt
"""
import json
import difflib
import sys
import os
import hashlib

def validate_prompt_integrity(prompt_hash: str) -> dict:
    """
    Valida integridade do prompt original
    
    Args:
        prompt_hash: Hash SHA-256 do prompt
        
    Returns:
        dict com status de validação
    """
    audit_file = f".buildtovalue/audit/prompt-{prompt_hash[:8]}.json"
    
    if not os.path.exists(audit_file):
        return {
            'valid': False,
            'reason': 'Arquivo de auditoria não encontrado',
            'severity': 'CRITICAL'
        }
    
    try:
        with open(audit_file, 'r') as f:
            audit_data = json.load(f)
        
        stored_hash = audit_data['signature']['hash']
        
        if stored_hash != prompt_hash:
            return {
                'valid': False,
                'reason': 'Hash do prompt não corresponde',
                'expected': prompt_hash,
                'actual': stored_hash,
                'severity': 'CRITICAL'
            }
        
        return {
            'valid': True,
            'timestamp': audit_data['signature']['timestamp'],
            'algorithm': audit_data['signature']['algorithm']
        }
        
    except Exception as e:
        return {
            'valid': False,
            'reason': f'Erro ao validar integridade: {str(e)}',
            'severity': 'HIGH'
        }

def calculate_divergence(text_a: str, text_b: str) -> float:
    """
    Calcula divergência semântica entre duas saídas
    
    Args:
        text_a: Texto da IA-A
        text_b: Texto da IA-B
        
    Returns:
        float: score de divergência (0.0 = idêntico, 1.0 = completamente diferente)
    """
    seq = difflib.SequenceMatcher(None, text_a, text_b)
    return round(1 - seq.ratio(), 3)

def main():
    if len(sys.argv) < 4:
        print("Uso: mpaa-validator.py <gen_output> <audit_output> <result_file> [prompt_hash]", 
              file=sys.stderr)
        sys.exit(1)
    
    gen_file = sys.argv[1]
    audit_file = sys.argv[2]
    result_file = sys.argv[3]
    prompt_hash = sys.argv[4] if len(sys.argv) > 4 else None
    
    # 1. Validar integridade do prompt (se fornecido)
    integrity_check = None
    if prompt_hash:
        integrity_check = validate_prompt_integrity(prompt_hash)
        
        if not integrity_check['valid']:
            result = {
                'status': 'REJECTED',
                'reason': 'Prompt integrity check failed',
                'integrity': integrity_check,
                'divergence_score': None,
                'decision': 'reject'
            }
            
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(1)
    
    # 2. Ler saídas das IAs
    with open(gen_file, 'r') as f:
        text_a = f.read()
    
    with open(audit_file, 'r') as f:
        text_b = f.read()
    
    # 3. Calcular divergência
    divergence = calculate_divergence(text_a, text_b)
    
    # 4. Aplicar regras de decisão
    threshold = float(os.getenv('BTV_MPAA_THRESHOLD', '0.25'))
    decision = 'approve' if divergence <= threshold else 'reject'
    
    # 5. Preparar resultado
    result = {
        'divergence_score': divergence,
        'threshold': threshold,
        'decision': decision,
        'integrity_check': integrity_check,
        'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'version': 'v7.4-platinum'
    }
    
    # 6. Salvar resultado
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # 7. Output para logs
    print(json.dumps(result, indent=2))
    
    return 0 if decision == 'approve' else 1

if __name__ == '__main__':
    sys.exit(main())