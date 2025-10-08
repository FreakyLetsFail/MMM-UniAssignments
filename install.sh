#!/bin/bash
# Installation Script für MMM-UniAssignments

set -e

echo "🔧 Installing MMM-UniAssignments..."

# Prüfe ob wir im richtigen Verzeichnis sind
if [ ! -f "MMM-UniAssignments.js" ]; then
    echo "❌ Error: MMM-UniAssignments.js not found. Please run from module directory."
    exit 1
fi

# Backend Installation
echo "📦 Setting up Python backend..."
cd backend

# Prüfe Python Version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Erstelle Virtual Environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Aktiviere Virtual Environment
source venv/bin/activate

# Installiere Python Dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Erstelle .env aus .env.example falls nicht vorhanden
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your TODOIST_API_TOKEN"
fi

cd ..

echo ""
echo "✅ MMM-UniAssignments installation completed!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Configure Todoist API Token:"
echo "   - Get your token from: https://todoist.com/prefs/integrations"
echo "   - Edit backend/.env and set TODOIST_API_TOKEN"
echo ""
echo "2. Start the backend server:"
echo "   ./start-backend.sh"
echo ""
echo "3. Add module to your MagicMirror config.js:"
echo ""
echo "   {"
echo "     module: 'MMM-UniAssignments',"
echo "     position: 'top_right',"
echo "     config: {"
echo "       backendUrl: 'http://localhost:5000',"
echo "       updateInterval: 300000  // 5 Minuten"
echo "     }"
echo "   }"
echo ""
echo "4. (Optional) Set up as systemd service:"
echo "   sudo ./setup-systemd.sh"
echo ""
