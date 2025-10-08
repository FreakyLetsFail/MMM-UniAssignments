#!/bin/bash
# Update Script für MMM-UniAssignments

set -e

echo "🔄 Updating MMM-UniAssignments..."

# Prüfe ob wir im richtigen Verzeichnis sind
if [ ! -f "MMM-UniAssignments.js" ]; then
    echo "❌ Error: MMM-UniAssignments.js not found."
    exit 1
fi

# Git pull (falls Git-Repo)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes..."
    git pull
fi

# Backend Update
echo "📦 Updating Python backend..."
cd backend

if [ -d "venv" ]; then
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
    deactivate
else
    echo "⚠️  Virtual environment not found. Run ./install.sh first."
fi

cd ..

echo ""
echo "✅ Update completed!"
echo ""
echo "📋 Next steps:"
echo "1. Restart backend service:"
echo "   sudo systemctl restart mmm-uni-assignments"
echo "2. Restart MagicMirror:"
echo "   pm2 restart MagicMirror"
echo ""
