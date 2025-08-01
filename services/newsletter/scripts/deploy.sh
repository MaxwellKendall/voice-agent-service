#!/bin/bash

# Newsletter Agent Deployment Script
# Supports Railway, Render, Vercel, and local Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_status "Please copy env.example to .env and fill in your API keys:"
        echo "cp env.example .env"
        echo "nano .env"
        exit 1
    fi
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    check_env
    railway login
    railway up
    print_success "Deployed to Railway!"
}


# Deploy webapp to Vercel
deploy_vercel() {
    print_status "Deploying webapp to Vercel..."
    
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not found. Please install it first:"
        echo "npm install -g vercel"
        exit 1
    fi
    
    cd webapp
    vercel --prod
    cd ..
    print_success "Webapp deployed to Vercel!"
}

# Deploy all to Railway + Vercel
deploy_all() {
    print_status "Deploying API to Railway and webapp to Vercel..."
    
    # Deploy API to Railway
    deploy_railway
    
    # Deploy webapp to Vercel
    deploy_vercel
    
    print_success "Full deployment complete!"
    print_status "API: Railway URL"
    print_status "Webapp: Vercel URL"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  railway    Deploy API to Railway"
    echo "  vercel     Deploy webapp to Vercel"
    echo "  all        Deploy API to Railway and webapp to Vercel"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 railway    # Deploy API to Railway"
    echo "  $0 vercel     # Deploy webapp to Vercel"
    echo "  $0 all        # Deploy both API and webapp"
}

# Main script
case "${1:-help}" in
    railway)
        deploy_railway
        ;;
    vercel)
        deploy_vercel
        ;;
    all)
        deploy_all
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac 