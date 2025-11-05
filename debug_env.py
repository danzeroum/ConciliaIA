import os
import sys

print("?? Debugando ambiente...")
print(f"Diret?rio atual: {os.getcwd()}")
print("Conte?do do diret?rio:")
for item in os.listdir('.'):
    print(f"  - {item}")

# Verificar se alembic.ini existe
ini_path = 'alembic.ini'
if os.path.exists(ini_path):
    print(f"? {ini_path} encontrado")
    with open(ini_path, 'r') as f:
        first_line = f.readline().strip()
        print(f"Primeira linha: {first_line}")
else:
    print(f"? {ini_path} n?o encontrado")
    # Listar diret?rios recursivamente
    print("Buscando arquivos .ini...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.ini'):
                print(f"Encontrado: {os.path.join(root, file)}")

# Verificar se a pasta alembic existe
alembic_dir = 'alembic'
if os.path.exists(alembic_dir) and os.path.isdir(alembic_dir):
    print(f"? Pasta {alembic_dir} encontrada")
    print(f"Conte?do de {alembic_dir}:")
    for item in os.listdir(alembic_dir):
        print(f"  - {item}")
else:
    print(f"? Pasta {alembic_dir} n?o encontrada")
