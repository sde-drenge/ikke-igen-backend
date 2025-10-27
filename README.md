# ikke-igen-backend

`psql postgres`

```
CREATE USER ikkeigen WITH PASSWORD 'ikkeigen';
ALTER ROLE ikkeigen SUPERUSER;
CREATE DATABASE ikkeigen;
GRANT ALL PRIVILEGES ON DATABASE ikkeigen TO ikkeigen;
\q
```
