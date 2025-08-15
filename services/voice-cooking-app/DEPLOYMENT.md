# Voice Cooking App - Deployment Guide

This guide covers deploying the Voice Cooking App to Vercel.

## Prerequisites

- Node.js 18+ installed
- Vercel account (free at [vercel.com](https://vercel.com))
- Supabase project with modern authentication
- Environment variables configured

## Quick Deployment

### Option 1: Using the Deployment Script

1. **Make the script executable** (if not already done):
   ```bash
   chmod +x deploy.sh
   ```

2. **Deploy to production**:
   ```bash
   ./deploy.sh --prod
   ```

3. **Deploy preview**:
   ```bash
   ./deploy.sh --preview
   ```

4. **Deploy to development**:
   ```bash
   ./deploy.sh --dev
   ```

### Option 2: Using npm Scripts

1. **Deploy to production**:
   ```bash
   npm run deploy
   ```

2. **Deploy preview**:
   ```bash
   npm run deploy:preview
   ```

3. **Deploy to development**:
   ```bash
   npm run deploy:dev
   ```

### Option 3: Manual Deployment

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

## Environment Variables Setup

Before deploying, you need to set up your environment variables in Vercel:

### Via Vercel Dashboard

1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add the following variables:

```
# Supabase Configuration (Modern Authentication)
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
SUPABASE_SECRET_KEY=your_supabase_secret_key
SUPABASE_JWT_SIGNING_KEY=your_supabase_jwt_signing_key

# OpenAI Configuration
VITE_OPENAI_API_KEY=your_openai_api_key

# Recipe Extraction API
VITE_RECIPE_API_URL=your_recipe_extraction_endpoint_url

# WebSocket Configuration
VITE_WEBSOCKET_URL=your_websocket_server_url
```

### Via Vercel CLI

```bash
vercel env add VITE_SUPABASE_URL
vercel env add VITE_SUPABASE_PUBLISHABLE_KEY
vercel env add SUPABASE_SECRET_KEY
vercel env add SUPABASE_JWT_SIGNING_KEY
vercel env add VITE_OPENAI_API_KEY
vercel env add VITE_RECIPE_API_URL
vercel env add VITE_WEBSOCKET_URL
```

## Configuration Files

### vercel.json
- Configures build settings and routing
- Sets up PWA service worker caching
- Configures security headers
- Handles SPA routing

### .vercelignore
- Excludes unnecessary files from deployment
- Reduces deployment size and time
- Excludes development and test files

## Deployment Features

### PWA Support
- Service worker for offline functionality
- App manifest for installability
- Proper caching strategies
- HTTPS required for PWA features

### Performance Optimizations
- Automatic code splitting
- Asset optimization
- CDN distribution
- Edge caching

### Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

## Post-Deployment

### Verify Deployment
1. Check the deployment URL provided by Vercel
2. Test PWA installation on mobile devices
3. Verify all features work correctly
4. Test responsive design across devices

### Custom Domain (Optional)
1. Go to Vercel project settings
2. Add your custom domain
3. Configure DNS settings
4. Enable HTTPS

### Monitoring
- Vercel provides built-in analytics
- Monitor performance metrics
- Check error logs
- Track user engagement

## Troubleshooting

### Common Issues

**Build Failures**
- Check environment variables are set
- Verify all dependencies are installed
- Check for TypeScript errors

**PWA Not Working**
- Ensure HTTPS is enabled
- Check service worker registration
- Verify manifest file is accessible

**Environment Variables Not Loading**
- Check variable names start with `VITE_` for client-side access
- Verify variables are set in Vercel dashboard
- Redeploy after adding new variables

**Supabase Authentication Issues**
- Verify you're using modern authentication keys (not legacy anon key)
- Check that Google OAuth is properly configured in Supabase
- Ensure redirect URLs are correctly set

### Getting Help

- Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
- Review build logs in Vercel dashboard
- Check browser console for client-side errors
- Verify network requests in browser dev tools

## Continuous Deployment

### GitHub Integration
1. Connect your GitHub repository to Vercel
2. Enable automatic deployments
3. Configure branch deployment rules
4. Set up preview deployments for PRs

### Environment-Specific Deployments
- Production: `main` branch
- Preview: `develop` branch
- Development: feature branches

## Cost Considerations

- Vercel Hobby plan: Free
- Includes 100GB bandwidth/month
- 100GB storage
- Automatic HTTPS
- Global CDN
- Serverless functions included

For higher usage, consider Vercel Pro or Enterprise plans.
