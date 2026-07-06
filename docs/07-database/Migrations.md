# Migrations.md

# TravelMate AI — Database Migrations

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Migration Framework

TravelMate AI uses **Alembic** (with SQLAlchemy) for PostgreSQL schema migrations.

**Principles:**
1. Never modify the database schema manually in production.
2. Migrations must be forward-only in production (rollbacks are tested, but rarely executed live; prefer roll-forward fixes).
3. Migrations must not lock active tables for extended periods.

---

## 2. Directory Structure

```
apps/api/app/infrastructure/database/
├── connection.py
├── models.py
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/
        ├── 001_initial_schema.py
        ├── 002_add_user_preferences.py
        └── 003_add_jsonb_index.py
```

---

## 3. Workflow

### 3.1 Creating a Migration

1. Modify the SQLAlchemy models in `models.py`.
2. Generate the migration script automatically:
   ```bash
   alembic revision --autogenerate -m "add_user_preferences"
   ```
3. **Review the generated file:** Alembic is not perfect. Ensure constraints, enums, and indexes are generated correctly.
4. If adding an index to a large table, modify the script to use `CONCURRENTLY`.

### 3.2 Applying Migrations

**Local Development:**
```bash
alembic upgrade head
```

**Production (CI/CD):**
Migrations are run automatically during the GitHub Actions deployment pipeline, *before* the new FastAPI pods are rolled out.

```bash
# In CI environment
DATABASE_URL=$PROD_DB_URL alembic upgrade head
```

---

## 4. Zero-Downtime Migrations

To achieve zero-downtime deployments, schema changes must be backward compatible with the currently running application version.

### 4.1 Adding a Column
1. Add column as `NULLABLE` (or with a `DEFAULT`).
2. Deploy code that writes to the new column.
3. (Later) Run backfill script if needed.
4. (Later) Add `NOT NULL` constraint if required.

### 4.2 Renaming a Column
1. Add new column.
2. Deploy code that writes to *both* columns, reads from old.
3. Backfill data from old to new.
4. Deploy code that reads/writes *only* to new column.
5. Drop old column.

### 4.3 Adding an Index
Always use `CONCURRENTLY` for production migrations to avoid locking the table against writes during index build.

```python
# In alembic version file
def upgrade():
    # Note: Requires execution outside of transaction
    op.execute("COMMIT")
    op.create_index('idx_trips_travel_date', 'trip_plans', ['travel_date'], postgresql_concurrently=True)
```
