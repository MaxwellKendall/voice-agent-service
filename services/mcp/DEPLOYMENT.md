# MCP Service Deployment Guide

This guide will help you deploy the MCP service to Railway using the free tier.

## 🚀 Quick Deploy

### Prerequisites
- Railway account (free tier)
- OpenAI API key
- MongoDB database (free tier available)
- Qdrant vector database (free tier available)

### Step 1: Setup Environment
```bash
cd services/mcp
./setup-env.sh
```

### Step 2: Deploy to Railway
```bash
./deploy.sh
```

## 📋 Detailed Steps

### 1. Database Setup

#### MongoDB Atlas (Free Tier)
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create free account
3. Create new cluster (M0 Free tier)
4. Create database user
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/database`

#### Qdrant Cloud (Free Tier)
1. Go to [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create free account
3. Create new cluster
4. Get API key and URL

### 2. Railway Deployment

#### Option A: Using Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to MCP service
cd services/mcp

# Initialize Railway project
railway init

# Deploy
railway up
```

#### Option B: Using Railway Dashboard
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository and `services/mcp` directory
5. Railway will automatically detect the Dockerfile

### 3. Environment Variables

Set these in Railway dashboard:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database
QDRANT_URL=https://your-qdrant-instance.cloud
QDRANT_API_KEY=your-qdrant-api-key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### 4. Verify Deployment

```bash
# Check deployment status
railway status

# View logs
railway logs

# Test health endpoint
curl https://your-app.railway.app/health
```

## 🔧 Configuration

### Railway Configuration
- **Builder**: Dockerfile
- **Port**: 8000
- **Health Check**: `/health`
- **Restart Policy**: On failure

### Environment Variables
All configuration is handled via environment variables. See `env.example` for the complete list.

## 📊 Monitoring

### Railway Dashboard
- View deployment status
- Monitor resource usage
- Check logs
- Manage environment variables

### Health Checks
The service includes a health endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "recipe-agent-mcp"
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Railway logs: `railway logs`
   - Verify Dockerfile syntax
   - Ensure all dependencies are in requirements.txt

2. **Database Connection Issues**
   - Verify MongoDB connection string
   - Check Qdrant URL and API key
   - Ensure databases are accessible from Railway

3. **API Key Issues**
   - Verify OpenAI API key is valid
   - Check API key permissions
   - Ensure key is set in Railway environment variables

### Debug Mode
Enable debug mode by setting `DEBUG=true` in Railway environment variables.

## 💰 Cost Optimization

### Free Tier Limits
- **Railway**: 500 hours/month
- **MongoDB Atlas**: 512MB storage
- **Qdrant Cloud**: Free tier available
- **OpenAI API**: Pay-per-use (minimal for MCP tools)

### Cost Monitoring
- Monitor Railway usage in dashboard
- Track OpenAI API usage
- Set up billing alerts

## 🔄 Updates

To update the deployment:
```bash
# Make your changes
git add .
git commit -m "Update MCP service"

# Deploy to Railway
railway up
```

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
