#!/bin/bash

# Script để chạy backend trong môi trường development

echo "🚀 Starting USITech Backend..."

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được cài đặt"
    exit 1
fi

# Kiểm tra pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 không được cài đặt"
    exit 1
fi

# Tạo virtual environment nếu chưa có
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Tạo file .env nếu chưa có
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp env.example .env
    echo "✅ Please update .env file with your database configuration"
fi

# Chạy server
echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/api/v1/docs"
echo "🔗 Health Check: http://localhost:8000/health"
echo ""

python run.py
