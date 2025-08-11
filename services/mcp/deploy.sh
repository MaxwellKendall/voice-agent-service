#!/bin/bash

# Railway Deployment Script for MCP Service
set -e

echo "🚀 Deploying MCP Service to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found. Make sure you're in the services/mcp directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. You'll need to set environment variables in Railway dashboard."
    echo "   Copy env.example to .env and fill in your values:"
    echo "   cp env.example .env"
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway login status..."
railway login

# Initialize Railway project (if not already initialized)
if [ ! -f ".railway" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set up environment variables in Railway dashboard:"
echo "   - OPENAI_API_KEY"
echo "   - MONGODB_URL"
echo "   - QDRANT_URL"
echo "   - QDRANT_API_KEY (if using cloud Qdrant)"
echo ""
echo "2. Get your deployment URL:"
echo "   railway status"
echo ""
echo "3. Test the health endpoint:"
echo "   curl https://your-app.railway.app/health"
echo ""
echo "4. View logs:"
echo "   railway logs"
