#!/bin/bash

# ====================================
# Fix Script Permissions
# ====================================

echo "🔧 Fixing script permissions..."

# Make all .sh files executable
find scripts/ -type f -name "*.sh" -exec chmod +x {} \;

# Make Python scripts executable if they have shebang
find scripts/ -type f -name "*.py" -exec grep -l "^#!/usr/bin/env python" {} \; | xargs chmod +x

echo "✅ Permissions fixed!"

# Show summary
echo ""
echo "📊 Summary:"
echo "  Shell scripts: $(find scripts/ -type f -name "*.sh" | wc -l)"
echo "  Python scripts: $(find scripts/ -type f -name "*.py" | wc -l)"
echo "  Executable: $(find scripts/ -type f -executable | wc -l)"
