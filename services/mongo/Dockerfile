# MongoDB Dockerfile
# Extends the official MongoDB image with custom configurations

FROM mongo:7.0

# Set environment variables for MongoDB
ENV MONGO_INITDB_ROOT_USERNAME=admin
ENV MONGO_INITDB_ROOT_PASSWORD=secret

# Create a custom MongoDB configuration file
RUN echo "security:\n  authorization: enabled" > /etc/mongod.conf

# Expose MongoDB port
EXPOSE 27017

# Create data directory
RUN mkdir -p /data/db

# Set proper permissions
RUN chown -R mongodb:mongodb /data/db

# Health check to ensure MongoDB is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD mongosh --eval "db.adminCommand('ping')" || exit 1

# Use the default MongoDB entrypoint and command
CMD ["mongod", "--config", "/etc/mongod.conf"]
