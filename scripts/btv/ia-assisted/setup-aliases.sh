#!/bin/bash
# BuildToValue v7.1 - Setup Aliases para IA-Assisted

SHELL_CONFIG=""

# Detectar shell
if [ -n "$ZSH_VERSION" ]; then
  SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
  SHELL_CONFIG="$HOME/.bashrc"
else
  echo "❌ Shell não suportado"
  exit 1
fi

echo "🔧 Configurando aliases para BuildToValue IA-Assisted..."
echo "Shell config: $SHELL_CONFIG"
echo ""

# Adicionar aliases
cat >> "$SHELL_CONFIG" << 'EOF'

# BuildToValue v7.1 - IA-Assisted Aliases
alias btv='./scripts/ia-assisted/manage-workflow.sh'
alias btv-gen='./scripts/ia-assisted/manage-workflow.sh generate'
alias btv-val='./scripts/ia-assisted/manage-workflow.sh validate'
alias btv-prep='./scripts/ia-assisted/manage-workflow.sh prepare'
alias btv-log='./scripts/ia-assisted/manage-workflow.sh log'
alias btv-rec='./scripts/ia-assisted/manage-workflow.sh recommend'

EOF

echo "✅ Aliases adicionados ao $SHELL_CONFIG"
echo ""
echo "Para ativar agora:"
echo "  source $SHELL_CONFIG"
echo ""
echo "Uso:"
echo "  btv-gen ia-developer 'Implementar X'"
echo "  btv-val ia-developer response.md"
echo "  btv-prep response.md"
echo "  btv-log claude 'Task' success 0.9"
echo "  btv-rec ia-developer"

