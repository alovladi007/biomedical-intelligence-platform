#!/bin/bash
#
# PostgreSQL Database Restore Script
# Restore from encrypted/compressed backups
#
# Usage: ./restore_database.sh <backup_file> [target_db]
#

set -e

# ============================================================================
# Configuration
# ============================================================================

BACKUP_FILE="$1"
TARGET_DB="${2:-biomedical_platform_restored}"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

ENCRYPTION_KEY="${ENCRYPTION_KEY:-/etc/postgresql/backup_key.gpg}"

LOG_FILE="/var/log/postgresql-backups/restore_$(date +%Y%m%d_%H%M%S).log"

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

# Validate inputs
validate_inputs() {
    if [ -z "$BACKUP_FILE" ]; then
        error "Backup file not specified. Usage: $0 <backup_file> [target_db]"
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
    fi

    log "Backup file: $BACKUP_FILE"
    log "Target database: $TARGET_DB"
}

# Decrypt backup if encrypted
decrypt_backup() {
    if [[ "$BACKUP_FILE" == *.gpg ]]; then
        log "Decrypting backup file..."

        local decrypted_file="${BACKUP_FILE%.gpg}"

        gpg --decrypt \
            --output "$decrypted_file" \
            "$BACKUP_FILE"

        if [ $? -eq 0 ]; then
            BACKUP_FILE="$decrypted_file"
            log "Backup decrypted: $BACKUP_FILE"
        else
            error "Decryption failed"
        fi
    fi
}

# Create target database
create_target_database() {
    log "Creating target database: $TARGET_DB"

    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -c "DROP DATABASE IF EXISTS $TARGET_DB;" \
        2>> "$LOG_FILE"

    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -c "CREATE DATABASE $TARGET_DB;" \
        2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Target database created successfully"
    else
        error "Failed to create target database"
    fi
}

# Restore database
restore_database() {
    log "Starting database restore..."

    PGPASSWORD="$DB_PASSWORD" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$TARGET_DB" \
        --verbose \
        --clean \
        --if-exists \
        "$BACKUP_FILE" \
        2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "Database restore completed successfully"
    else
        error "Database restore failed"
    fi
}

# Verify restore
verify_restore() {
    log "Verifying restored database..."

    local table_count=$(PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$TARGET_DB" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" \
        2>> "$LOG_FILE" | tr -d ' ')

    log "Tables restored: $table_count"

    if [ "$table_count" -gt 0 ]; then
        log "Database verification successful"
    else
        error "Database verification failed - no tables found"
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log "========================================="
    log "PostgreSQL Database Restore"
    log "========================================="

    validate_inputs
    decrypt_backup
    create_target_database
    restore_database
    verify_restore

    log "========================================="
    log "Restore completed successfully"
    log "Database: $TARGET_DB"
    log "========================================="
}

main
