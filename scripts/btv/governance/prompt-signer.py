#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum - Prompt Integrity Signer
Gera hash SHA-256 de prompts para validação de integridade
"""
import sys
import hashlib
import json
import os
from datetime import datetime

def sign_prompt(prompt: str) -> dict:
    """
    Assina um prompt com SHA-256 e metadados
    
    Args:
        prompt: Texto do prompt a ser assinado
        
    Returns:
        dict com hash, timestamp e metadados
    """
    # Normalizar prompt (remover espaços extras)
    normalized = ' '.join(prompt.split())
    
    # Gerar hash
    prompt_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    # Metadados
    signature = {
        'hash': prompt_hash,
        'algorithm': 'sha256',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'length': len(normalized),
        'version': 'v7.4-platinum'
    }
    
    return signature

def verify_prompt(prompt: str, expected_hash: str) -> bool:
    """
    Verifica se um prompt corresponde ao hash esperado
    
    Args:
        prompt: Texto do prompt
        expected_hash: Hash esperado
        
    Returns:
        True se válido, False caso contrário
    """
    signature = sign_prompt(prompt)
    return signature['hash'] == expected_hash

def main():
    if len(sys.argv) < 2:
        print("Uso: prompt-signer.py <prompt>", file=sys.stderr)
        sys.exit(1)
    
    prompt = sys.argv[1]
    signature = sign_prompt(prompt)
    
    # Salvar assinatura em arquivo de auditoria
    audit_dir = '.buildtovalue/audit'
    os.makedirs(audit_dir, exist_ok=True)
    
    audit_file = f"{audit_dir}/prompt-{signature['hash'][:8]}.json"
    with open(audit_file, 'w') as f:
        json.dump({
            'prompt': prompt,
            'signature': signature
        }, f, indent=2)
    
    # Retornar apenas o hash para uso em scripts
    print(signature['hash'])
    
    return 0

if __name__ == '__main__':
    sys.exit(main())