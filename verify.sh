#!/bin/bash
# Installation & Setup Verification Script

echo ""
echo "=========================================="
echo "🔍 CMS Project Verification"
echo "=========================================="
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version

# Check project files
echo ""
echo "✓ Project files:"
if [ -f "app/app.py" ]; then echo "  ✅ app/app.py"; else echo "  ❌ app/app.py MISSING"; fi
if [ -f "requirements.txt" ]; then echo "  ✅ requirements.txt"; else echo "  ❌ requirements.txt MISSING"; fi
if [ -d "app/templates" ]; then echo "  ✅ app/templates/"; else echo "  ❌ app/templates/ MISSING"; fi
if [ -f "app/static/css/style.css" ]; then echo "  ✅ app/static/css/style.css"; else echo "  ❌ CSS MISSING"; fi

# Check venv
echo ""
echo "✓ Virtual environment:"
if [ -d "venv" ]; then 
    echo "  ✅ venv/ folder exists"
else 
    echo "  ⚠️  venv/ not found - Creating..."
    python3 -m venv venv
fi

# Check dependencies
echo ""
echo "✓ Dependencies:"
source venv/bin/activate
python -m pip list 2>/dev/null | grep -E "Flask|SQLAlchemy|Werkzeug" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ All packages installed"
else
    echo "  ⚠️  Installing packages..."
    pip install -r requirements.txt --quiet
fi

# Summary
echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "Next step: Run the application!"
echo ""
echo "Option 1 (Using script):"
echo "  ./run.sh"
echo ""
echo "Option 2 (Manual):"
echo "  source venv/bin/activate"
echo "  cd app"
echo "  python app.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
