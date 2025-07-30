# MongoDB Migration Guide

This guide explains how to migrate your local MongoDB data to a cloud-based MongoDB instance using the official MongoDB tools.

## Prerequisites

### 1. Install MongoDB Database Tools

**macOS:**
```bash
brew install mongodb/brew/mongodb-database-tools
```

**Ubuntu/Debian:**
```bash
sudo apt-get install mongodb-database-tools
```

**Windows:**
Download from [MongoDB Database Tools](https://www.mongodb.com/try/download/database-tools)

### 2. Verify Installation
```bash
mongodump --version
mongorestore --version
```

## Quick Start

### Option 1: One-Step Migration (Recommended)
```bash
# Migrate directly from local to cloud MongoDB
make mongo-migrate TARGET_URI="mongodb+srv://username:password@cluster.mongodb.net" TARGET_DB="newsletter_prod"
```

### Option 2: Two-Step Migration
```bash
# Step 1: Dump local database
make mongo-dump

# Step 2: Restore to cloud database
make mongo-restore TARGET_URI="mongodb+srv://username:password@cluster.mongodb.net" TARGET_DB="newsletter_prod"
```

### Option 3: Manual Commands
```bash
# Dump local database
./scripts/migrate_mongodb.sh dump ./backup

# Restore to cloud database
./scripts/migrate_mongodb.sh restore ./backup "mongodb+srv://username:password@cluster.mongodb.net" newsletter_prod

# Or do both in one step
./scripts/migrate_mongodb.sh migrate "mongodb+srv://username:password@cluster.mongodb.net" newsletter_prod
```

## Configuration

### Environment Variables

You can customize the migration by setting these environment variables:

```bash
# Source database configuration
export SOURCE_URI="mongodb://localhost:27017"
export SOURCE_DB="newsletter_agent"

# Dump directory (for manual dumps)
export DUMP_DIR="./mongodb_dump"
```

### Default Values

- **Source URI**: `mongodb://localhost:27017`
- **Source Database**: `newsletter_agent`
- **Dump Directory**: `./mongodb_dump`

## Cloud MongoDB Providers

### MongoDB Atlas
```bash
# Example Atlas connection string
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net
```

### AWS DocumentDB
```bash
# Example DocumentDB connection string
mongodb://username:password@cluster.cluster-xxxxx.region.docdb.amazonaws.com:27017
```

### Google Cloud Firestore
```bash
# Example Firestore connection string
mongodb://username:password@cluster.xxxxx.firestore.googleapis.com:27017
```

## Examples

### Migrate to MongoDB Atlas
```bash
make mongo-migrate TARGET_URI="mongodb+srv://myuser:mypassword@cluster0.abc123.mongodb.net" TARGET_DB="newsletter_production"
```

### Migrate to AWS DocumentDB
```bash
make mongo-migrate TARGET_URI="mongodb://myuser:mypassword@cluster.cluster-abc123.us-east-1.docdb.amazonaws.com:27017" TARGET_DB="newsletter_prod"
```

### Migrate with Custom Source Database
```bash
SOURCE_DB="my_custom_db" make mongo-migrate TARGET_URI="mongodb+srv://user:pass@cluster.mongodb.net" TARGET_DB="newsletter_prod"
```

## Troubleshooting

### Common Issues

#### 1. Connection Timeout
```
Error: connection() : timed out
```
**Solution**: Check your network connection and firewall settings. For cloud databases, ensure your IP is whitelisted.

#### 2. Authentication Failed
```
Error: Authentication failed
```
**Solution**: Verify your username and password. For MongoDB Atlas, ensure you're using the correct database user.

#### 3. Database Not Found
```
Error: database newsletter_agent not found
```
**Solution**: Check that your local database exists and the name is correct.

#### 4. Permission Denied
```
Error: not authorized on newsletter_agent to execute command
```
**Solution**: Ensure your MongoDB user has read permissions for the source database and write permissions for the target database.

### Debug Mode

For more detailed output, you can run the commands with verbose logging:

```bash
# The script already includes --verbose flag, but you can also check the logs
tail -f migration.log
```

### Verify Migration

After migration, verify the data was transferred correctly:

```bash
# Connect to your cloud database and check collections
mongosh "mongodb+srv://username:password@cluster.mongodb.net/newsletter_prod"
> show collections
> db.chats.countDocuments()
> db.messages.countDocuments()
```

## Security Best Practices

1. **Use Environment Variables**: Don't hardcode connection strings in scripts
2. **Network Security**: Use VPN or IP whitelisting for cloud databases
3. **Credentials**: Use strong passwords and rotate them regularly
4. **Encryption**: Ensure your connection uses TLS/SSL
5. **Backup**: Always keep a backup before migration

## Performance Tips

1. **Batch Size**: For large datasets, consider adjusting the batch size
2. **Network**: Use a fast, stable internet connection
3. **Timing**: Run migrations during off-peak hours
4. **Monitoring**: Monitor the migration progress and system resources

## What Gets Migrated

The migration script transfers:

- **Collections**: All collections in your source database
- **Documents**: All documents with their original structure
- **Indexes**: Database indexes (if supported by target)
- **Metadata**: Collection metadata and statistics

## Rollback Plan

If something goes wrong, you can restore from your local database:

```bash
# Your local database remains unchanged during migration
# If you need to rollback, simply re-run the migration
make mongo-migrate TARGET_URI="your_cloud_uri" TARGET_DB="your_target_db"
```

## Support

If you encounter issues:

1. Check the migration logs in `migration.log`
2. Verify your MongoDB tools are up to date
3. Test your connection strings manually
4. Check the MongoDB documentation for your specific cloud provider 