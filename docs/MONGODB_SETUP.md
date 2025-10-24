# MongoDB Setup

## Using Docker Compose (Recommended)

The easiest way to run MongoDB for development and testing is using the provided Docker Compose configuration.

### Start MongoDB

```bash
# Start MongoDB and MongoDB Express (optional web UI)
docker-compose up -d

# Or start only MongoDB
docker-compose up -d mongodb
```

### Stop MongoDB

```bash
docker-compose down
```

### Access MongoDB

- **MongoDB**: `mongodb://memori:memori@localhost:27017/memori`
- **Test Database**: `mongodb://memori:memori@localhost:27017/memori_test`
- **MongoDB Express UI**: http://localhost:8081 (optional)

## Manual Installation

### macOS

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

### Linux

```bash
# Import the public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Create Databases and Users

```bash
# Connect to MongoDB
mongosh

# Create memori database and user
use memori
db.createUser({
  user: 'memori',
  pwd: 'memori',
  roles: [{ role: 'readWrite', db: 'memori' }]
})

# Create test database and user
use memori_test
db.createUser({
  user: 'memori',
  pwd: 'memori',
  roles: [{ role: 'readWrite', db: 'memori_test' }]
})
```

## Verify Setup

```bash
# Test MongoDB migrations
uv run tests/build/mongodb.py
```

Should output:
```
+ Building revision #1...
    create collection memori_schema_version
    create collection memori_parent
    ...
+ Build executed successfully!
✓ Collection memori_schema_version exists
✓ Collection memori_parent exists
...
```

## Connection Strings

### Development
```
mongodb://memori:memori@localhost:27017/memori
```

### Testing
```
mongodb://memori:memori@localhost:27017/memori_test
```

### Docker Compose
```
mongodb://memori:memori@mongodb:27017/memori
```

## Troubleshooting

**Connection issues:**
```bash
# Check if MongoDB is running
docker-compose ps

# Restart MongoDB
docker-compose restart mongodb

# View MongoDB logs
docker-compose logs mongodb
```

**Reset test database:**
```bash
# Using Docker Compose
docker-compose exec mongodb mongosh --eval "db = db.getSiblingDB('memori_test'); db.dropDatabase()"

# Using local installation
mongosh memori_test --eval "db.dropDatabase()"
```

**Reset all data:**
```bash
docker-compose down -v
docker-compose up -d
```

## MongoDB Express (Web UI)

MongoDB Express is included in the Docker Compose setup and provides a web-based interface for managing MongoDB.

- **URL**: http://localhost:8081
- **No authentication required** (configured for development only)
- **MongoDB Connection**: Uses admin:memori credentials to connect to MongoDB
- **Configuration**: Basic authentication is disabled for development convenience

## Production Considerations

For production deployments, consider:

1. **Security**: Change default passwords and enable authentication
2. **Networking**: Use proper network security groups/firewalls
3. **Persistence**: Configure proper volume mounts for data persistence
4. **Monitoring**: Set up MongoDB monitoring and alerting
5. **Backup**: Implement regular backup strategies
6. **SSL/TLS**: Enable encrypted connections

## Environment Variables

The Docker Compose setup uses the following environment variables:

- `MONGO_INITDB_ROOT_USERNAME`: Root username (default: admin)
- `MONGO_INITDB_ROOT_PASSWORD`: Root password (default: memori)
- `MONGO_INITDB_DATABASE`: Initial database (default: memori)