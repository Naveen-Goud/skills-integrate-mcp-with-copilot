# Database Implementation

This document describes the persistent database layer added to the Mergington High School Activities API.

## Overview

The application now uses SQLAlchemy ORM with SQLite (development) for persistent data storage. All data survives application restarts.

## Architecture

### Database Layer
- **database.py**: Database configuration, connection setup, and session management
- **models.py**: SQLAlchemy ORM models (Activity, Participant)
- **backup.py**: Backup and recovery utilities

### Models

#### Activity
```python
- id: Primary key
- name: Unique activity name
- description: Activity description
- schedule: When the activity meets
- max_participants: Maximum capacity
- participants: Relationship to Participant records
```

#### Participant
```python
- id: Primary key
- email: Student email
- activity_id: Foreign key to Activity
- activity: Relationship to Activity
```

## Features

### ✅ Data Persistence
- All data persists across application restarts
- SQLite database file: `activities.db`

### ✅ Database Models
- Proper relational schema with foreign keys
- Enforced data integrity constraints
- Cascade deletes (deleting an activity removes its participants)

### ✅ Data Integrity
- Unique constraint prevents duplicate registrations
- Foreign key constraints maintain referential integrity
- Transactional operations ensure consistency

### ✅ Backup & Recovery
- JSON-based backup functionality in `backup.py`
- Point-in-time recovery capabilities
- Timestamped backup files for audit trail

## Usage

### Setup
```bash
pip install -r requirements.txt
cd src
python app.py
```

The database will automatically:
1. Initialize on first startup
2. Load sample data if empty
3. Create tables with proper schema

### Creating Backups

```python
from database import SessionLocal
from backup import backup_database

db = SessionLocal()
backup_path = backup_database(db)
db.close()
```

### Restoring from Backup

```python
from database import SessionLocal
from backup import restore_database

db = SessionLocal()
restore_database(db, "backups/backup_20260813_120000.json")
db.close()
```

### Database Migrations

The current implementation uses simple schema initialization. For production:

1. **Setup Alembic** (already in requirements.txt):
   ```bash
   alembic init migrations
   ```

2. **Create initial migration**:
   ```bash
   alembic revision --autogenerate -m "initial schema"
   ```

3. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

## Environment Configuration

To use PostgreSQL instead of SQLite:

```bash
export DATABASE_URL="postgresql://user:password@localhost/mergington_activities"
python app.py
```

## Data Persistence Across Deployments

The current implementation ensures:
- ✅ All activities and registrations persist
- ✅ Data survives server restarts
- ✅ No more in-memory data loss
- ✅ Production-ready for larger datasets
- ✅ Easy to switch to PostgreSQL for production

## Next Steps

For production deployment:
1. Switch to PostgreSQL for reliability and performance
2. Implement automated backups
3. Set up database replication/failover
4. Configure connection pooling (already built into SQLAlchemy)
