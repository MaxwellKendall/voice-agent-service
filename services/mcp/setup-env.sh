#!/bin/bash

# Environment Setup Script for MCP Service
set -e

echo "🔧 Setting up environment for MCP Service..."

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found. Make sure you're in the services/mcp directory."
    exit 1
fi

# Copy env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and fill in your API keys and database URLs:"
    echo "   - OPENAI_API_KEY: Your OpenAI API key"
    echo "   - MONGODB_URL: Your MongoDB connection string"
    echo "   - QDRANT_URL: Your Qdrant instance URL"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "📋 Required Environment Variables:"
echo ""
echo "🔑 OpenAI Configuration:"
echo "   OPENAI_API_KEY=sk-..."
echo "   OPENAI_MODEL=gpt-4"
echo "   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002"
echo ""
echo "🗄️  Database Configuration:"
echo "   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database"
echo "   QDRANT_URL=https://your-qdrant-instance.cloud"
echo "   QDRANT_API_KEY=your-qdrant-api-key"
echo ""
echo "🌐 Server Configuration:"
echo "   HOST=0.0.0.0"
echo "   PORT=8000"
echo "   DEBUG=false"
echo ""
echo "📊 For Railway deployment, set these in the Railway dashboard:"
echo "   railway variables set OPENAI_API_KEY=your-key"
echo "   railway variables set MONGODB_URL=your-mongodb-url"
echo "   railway variables set QDRANT_URL=your-qdrant-url"
echo ""
echo "🔗 Free Database Options:"
echo "   - MongoDB Atlas: https://www.mongodb.com/atlas (Free tier: 512MB)"
echo "   - Qdrant Cloud: https://cloud.qdrant.io/ (Free tier available)"
echo "   - Or deploy Qdrant on Railway as a separate service"
