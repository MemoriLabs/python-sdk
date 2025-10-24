// MongoDB initialization script for Memori SDK
// This script creates the necessary databases and users for development and testing

// Switch to memori database
db = db.getSiblingDB('memori');

// Create application user for memori database
db.createUser({
  user: 'memori',
  pwd: 'memori',
  roles: [
    {
      role: 'readWrite',
      db: 'memori'
    }
  ]
});

// Create test database
db = db.getSiblingDB('memori_test');

// Create application user for test database
db.createUser({
  user: 'memori',
  pwd: 'memori',
  roles: [
    {
      role: 'readWrite',
      db: 'memori_test'
    }
  ]
});

print('MongoDB initialization completed successfully!');
print('Databases created: memori, memori_test');
print('Users created: memori (with readWrite access to both databases)');
