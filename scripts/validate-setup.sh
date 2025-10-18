#!/bin/bash

echo "🔍 Validating BuildToValue v7 Setup..."
echo ""

errors=0

# Check required files
echo "📄 Checking required files..."
files=(
    ".env.example"
    "requirements.txt"
    "requirements-dev.txt"
    "Makefile"
    "pyproject.toml"
    ".gitignore"
    "docker-compose.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
        ((errors++))
    fi
done

echo ""

# Check script permissions
echo "🔧 Checking script permissions..."
non_executable=$(find scripts/ -name "*.sh" ! -executable | wc -l)
if [ "$non_executable" -eq 0 ]; then
    echo "  ✅ All scripts are executable"
else
    echo "  ❌ $non_executable scripts are not executable"
    echo "  Run: ./scripts/fix-permissions.sh"
    ((errors++))
fi

echo ""

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if pip3 list | grep -q "fastapi"; then
    echo "  ✅ Dependencies installed"
else
    echo "  ⚠️  Dependencies not installed"
    echo "  Run: pip3 install -r requirements.txt"
fi

echo ""

# Summary
if [ $errors -eq 0 ]; then
    echo "✅ Validation passed! Setup is complete."
    exit 0
else
    echo "❌ Validation failed with $errors errors"
    echo "Please fix the issues above"
    exit 1
fi
