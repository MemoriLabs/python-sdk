# PostgreSQL Setup

## Install PostgreSQL

**macOS:**
```bash
brew install postgresql@17
brew services start postgresql@17
echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Create Databases

```bash
createdb memori
createdb memori_test
psql -d memori -c "CREATE USER memori WITH PASSWORD 'memori';"
psql -d memori -c "GRANT ALL PRIVILEGES ON DATABASE memori TO memori;"
psql -d memori -c "GRANT ALL ON SCHEMA public TO memori;"
psql -d memori_test -c "GRANT ALL ON SCHEMA public TO memori;"
```

## Verify Setup

```bash
uv run python tests/build/postgresql.py
```

Should output:
```
+ Building revision #1...
    create table memori_schema_version
    create table memori_parent
    ...
+ Build executed successfully!
```

## Troubleshooting

**Connection issues:**
```bash
brew services restart postgresql@17  # macOS
sudo systemctl restart postgresql     # Linux
```

**Reset test database:**
```bash
dropdb memori_test && createdb memori_test
psql -d memori_test -c "GRANT ALL ON SCHEMA public TO memori;"
```
