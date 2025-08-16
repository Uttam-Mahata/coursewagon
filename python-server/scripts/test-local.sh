#!/bin/bash

# Test CourseWagon Backend Locally with Azure Storage

echo "🧪 Testing CourseWagon Backend with Azure Storage"
echo "================================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source /home/uttam/CourseWagon/.venv/bin/activate
fi

echo "✅ Virtual environment activated"

# Test Azure Storage integration
echo "1️⃣  Testing Azure Storage integration..."
python test_azure_storage.py

if [ $? -eq 0 ]; then
    echo "✅ Azure Storage test passed!"
else
    echo "❌ Azure Storage test failed!"
    exit 1
fi

# Test if the Flask app can start
echo "2️⃣  Testing Flask application startup..."
echo "   Starting server on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the Flask app
python app.py
