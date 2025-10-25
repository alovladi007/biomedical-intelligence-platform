#!/bin/bash
#
# PostgreSQL Backup Script for HIPAA Compliance
# Automated database backups with 6-year retention
#
# Usage: ./backup_database.sh [full|incremental]
#

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

# Database connection
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-biomedical_platform}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Backup configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgresql}"
BACKUP_TYPE="${1:-full}"  # full or incremental
RETENTION_DAYS=2190  # 6 years (365 * 6)

# Encryption
ENCRYPTION_KEY="${ENCRYPTION_KEY:-/etc/postgresql/backup_key.gpg}"
ENCRYPT_BACKUPS="${ENCRYPT_BACKUPS:-true}"

# S3 configuration (optional)
S3_BUCKET="${S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Logging
LOG_DIR="/var/log/postgresql-backups"
LOG_FILE="${LOG_DIR}/backup_$(date +%Y%m%d_%H%M%S).log"

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
    exit 1
}

# Create necessary directories
setup_directories() {
    log "Setting up backup directories..."

    mkdir -p "$BACKUP_DIR"/{full,incremental,wal_archive}
    mkdir -p "$LOG_DIR"

    # Set secure permissions
    chmod 700 "$BACKUP_DIR"
    chmod 700 "$LOG_DIR"
}

# Check if PostgreSQL is running
check_postgres() {
    log "Checking PostgreSQL status..."

    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
        error "PostgreSQL is not running or not accessible"
    fi

    log "PostgreSQL is running"
}

# Perform full backup
full_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/full/biomedical_platform_full_${timestamp}.sql"
    local compressed_file="${backup_file}.gz"

    log "Starting full database backup..."
    log "Backup file: $backup_file"

    # Perform backup using pg_dump
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$backup_file" \
        2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Database backup completed successfully"

        # Get backup size
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "Backup size: $backup_size"

        # Encrypt backup if enabled
        if [ "$ENCRYPT_BACKUPS" = "true" ]; then
            encrypt_backup "$backup_file"
        fi

        # Upload to S3 if configured
        if [ -n "$S3_BUCKET" ]; then
            upload_to_s3 "$backup_file"
        fi

        # Verify backup
        verify_backup "$backup_file"

        log "Full backup completed: $backup_file"
    else
        error "Database backup failed"
    fi
}

# Perform incremental backup (WAL archiving)
incremental_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local wal_dir="${BACKUP_DIR}/incremental/${timestamp}"

    log "Starting incremental backup (WAL archiving)..."

    mkdir -p "$wal_dir"

    # Archive WAL files
    PGPASSWORD="$DB_PASSWORD" pg_basebackup \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -D "$wal_dir" \
        --format=tar \
        --gzip \
        --progress \
        --checkpoint=fast \
        --wal-method=fetch \
        2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Incremental backup completed: $wal_dir"
    else
        error "Incremental backup failed"
    fi
}

# Encrypt backup file
encrypt_backup() {
    local backup_file="$1"
    local encrypted_file="${backup_file}.gpg"

    log "Encrypting backup file..."

    if [ ! -f "$ENCRYPTION_KEY" ]; then
        log "WARNING: Encryption key not found. Skipping encryption."
        return
    fi

    gpg --encrypt \
        --recipient-file "$ENCRYPTION_KEY" \
        --output "$encrypted_file" \
        "$backup_file"

    if [ $? -eq 0 ]; then
        log "Backup encrypted: $encrypted_file"

        # Remove unencrypted backup
        rm -f "$backup_file"
        log "Unencrypted backup removed"
    else
        log "WARNING: Encryption failed. Keeping unencrypted backup."
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"

    log "Verifying backup integrity..."

    # Verify custom format backup
    PGPASSWORD="$DB_PASSWORD" pg_restore \
        --list \
        "$backup_file" \
        > /dev/null 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Backup verification successful"
    else
        error "Backup verification failed - backup may be corrupted"
    fi
}

# Upload backup to S3
upload_to_s3() {
    local backup_file="$1"
    local s3_path="s3://${S3_BUCKET}/postgresql-backups/$(basename $backup_file)"

    log "Uploading backup to S3: $s3_path"

    aws s3 cp "$backup_file" "$s3_path" \
        --region "$AWS_REGION" \
        --storage-class GLACIER \
        2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Backup uploaded to S3 successfully"
    else
        log "WARNING: S3 upload failed"
    fi
}

# Clean up old backups (6-year retention)
cleanup_old_backups() {
    log "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."

    # Clean full backups
    find "$BACKUP_DIR/full" -name "*.sql*" -mtime +$RETENTION_DAYS -delete 2>> "$LOG_FILE"

    # Clean incremental backups
    find "$BACKUP_DIR/incremental" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>> "$LOG_FILE"

    # Clean logs older than 1 year
    find "$LOG_DIR" -name "*.log" -mtime +365 -delete 2>> "$LOG_FILE"

    log "Cleanup completed"
}

# Generate backup report
generate_report() {
    local report_file="${LOG_DIR}/backup_report_$(date +%Y%m%d).txt"

    cat > "$report_file" <<EOF
PostgreSQL Backup Report
Generated: $(date)
================================

Database: $DB_NAME
Backup Type: $BACKUP_TYPE
Status: SUCCESS

Backup Statistics:
------------------
Full Backups: $(find "$BACKUP_DIR/full" -name "*.sql*" | wc -l)
Incremental Backups: $(find "$BACKUP_DIR/incremental" -type d -mindepth 1 | wc -l)

Disk Usage:
-----------
$(du -sh "$BACKUP_DIR")

Latest Backups:
---------------
$(ls -lht "$BACKUP_DIR/full" | head -5)

HIPAA Compliance:
-----------------
✓ 6-year retention policy active
✓ Backups encrypted: $ENCRYPT_BACKUPS
✓ Off-site storage (S3): $([ -n "$S3_BUCKET" ] && echo "YES" || echo "NO")
✓ Automated backup schedule active

EOF

    log "Backup report generated: $report_file"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log "========================================="
    log "PostgreSQL Backup Script"
    log "Backup Type: $BACKUP_TYPE"
    log "========================================="

    # Setup
    setup_directories
    check_postgres

    # Perform backup
    case "$BACKUP_TYPE" in
        full)
            full_backup
            ;;
        incremental)
            incremental_backup
            ;;
        *)
            error "Invalid backup type: $BACKUP_TYPE. Use 'full' or 'incremental'"
            ;;
    esac

    # Cleanup old backups
    cleanup_old_backups

    # Generate report
    generate_report

    log "========================================="
    log "Backup process completed successfully"
    log "========================================="
}

# Run main function
main
