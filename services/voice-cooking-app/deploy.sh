#!/bin/bash

# Voice Cooking App Deployment Script
# This script handles deployment to Vercel

set -e

echo "🚀 Starting Voice Cooking App deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the voice-cooking-app directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building the project..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed: dist directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
if [ "$1" = "--prod" ]; then
    echo "📤 Deploying to production..."
    vercel --prod
elif [ "$1" = "--preview" ]; then
    echo "📤 Deploying preview..."
    vercel
else
    echo "📤 Deploying to development..."
    vercel --dev
fi

echo "✅ Deployment completed!"
echo "🌐 Your app should be live at the URL provided above"
