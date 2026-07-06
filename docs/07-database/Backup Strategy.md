# Backup Strategy.md

# TravelMate AI — Database Backup Strategy

**Version:** 1.0.0  
**Date:** 2026-07-03

---

## 1. Objectives

- **Recovery Point Objective (RPO):** < 1 hour
- **Recovery Time Objective (RTO):** < 4 hours
- **Data Retention:** 30 days (daily backups), 12 months (monthly backups)

---

## 2. Backup Methods

### 2.1 Automated Provider Backups (Railway)
Railway automatically takes volume snapshots for the PostgreSQL database.
- **Frequency:** Daily
- **Retention:** 7 days
- **Type:** Full snapshot (Filesystem level)

### 2.2 Logical Backups (pg_dump)
For point-in-time recovery and off-site storage, a cron job executes logical backups.
- **Frequency:** Hourly (Incremental WAL archive), Daily (Full pg_dump)
- **Tool:** WAL-G or pgBackRest
- **Destination:** AWS S3 (ap-south-1 region for data residency)

---

## 3. Storage and Retention

Backups are stored in an S3 bucket configured with lifecycle policies:

| Backup Type | Frequency | S3 Storage Class | Retention Policy |
|---|---|---|---|
| Daily Full Backup | 1x / day | Standard | 30 days |
| Weekly Full Backup | 1x / week | Standard-IA (Infrequent Access) | 90 days |
| Monthly Full Backup | 1x / month | Glacier Deep Archive | 12 months |
| WAL Archives | Continuous | Standard | 7 days |

---

## 4. Security

- **Encryption at Rest:** S3 bucket uses SSE-S3 (AES-256) encryption.
- **Encryption in Transit:** All transfers to S3 occur over TLS.
- **Access Control:** The S3 bucket policy denies public access. Only the backup service IAM role has `s3:PutObject` permission. No delete permissions granted (WORM compliance via Object Lock).

---

## 5. Recovery Procedure

### 5.1 Restoring a Full Database (Disaster Recovery)

1. Provision a new PostgreSQL instance on Railway.
2. Download the latest daily `pg_dump` from S3.
3. Apply the dump:
   ```bash
   pg_restore -d $NEW_DB_URL travelmate_backup_2026-07-03.dump
   ```
4. Update the `DATABASE_URL` environment variable for the FastAPI service.
5. Restart the FastAPI service.

### 5.2 Point-in-Time Recovery (PITR)

If data is accidentally deleted (e.g., at 14:00):
1. Restore the daily full backup from 00:00 to a temporary database.
2. Apply WAL archives up to 13:59.
3. Export the needed data (e.g., specific user records).
4. Re-import into the primary production database.

---

## 6. Testing

Backups must be tested quarterly to ensure they can be successfully restored.

**Procedure:**
1. Spin up a staging database.
2. Restore the latest production backup.
3. Run the application test suite against the staging database.
4. Verify data integrity (trip counts match expected totals).
5. Destroy the staging database.
6. Log the test result in the compliance register.
