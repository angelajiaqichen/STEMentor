#!/bin/bash

# AI Learning Platform - Development Setup Script

set -e

echo "🚀 Setting up AI Learning Platform for development..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and Docker Compose first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p database/data
mkdir -p logs

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up -d postgres redis chromadb

echo "⏳ Waiting for services to be ready..."
sleep 10

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in backend directory"
    exit 1
fi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi
npm install --legacy-peer-deps
cd ..

# Run database migrations
echo "🗃️  Running database migrations..."
cd backend
source venv/bin/activate
# alembic upgrade head  # Uncomment when you have migrations
cd ..

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit the .env file with your API keys and configuration"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && npm start"
echo "4. Visit http://localhost:3000 to access the application"
echo ""
echo "🔧 Available services:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
echo "- ChromaDB: http://localhost:8000"
