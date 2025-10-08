#!/bin/bash
# Start Script für Flask Backend

cd backend

# Aktiviere Virtual Environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Prüfe .env
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run ./install.sh first."
    exit 1
fi

echo "🚀 Starting MMM-UniAssignments Backend..."
python3 app.py
