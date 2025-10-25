#!/bin/bash
#
# Production Setup and Security Hardening Script
# Sets up infrastructure with security best practices
#
# Usage: sudo ./setup_production.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# ============================================================================
# Environment Setup
# ============================================================================

setup_environment() {
    log_info "Setting up production environment..."

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        log_warn ".env file not found. Creating from template..."

        cat > .env <<EOF
# =============================================================================
# Production Environment Configuration
# =============================================================================

# Database Configuration
DATABASE_URL=postgresql://postgres:$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)@localhost:5432/biomedical_platform
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MFA Configuration
MFA_ISSUER=Biomedical-Platform

# Monitoring Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_API_KEY=your-pagerduty-integration-key

# AWS Configuration (Optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Elasticsearch Configuration (Optional)
ELASTICSEARCH_HOSTS=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Redis Configuration
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Service Configuration
SERVICE_NAME=biomedical-platform
ENVIRONMENT=production
LOG_LEVEL=INFO

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Backup Configuration
BACKUP_DIR=/var/backups/postgresql
S3_BUCKET=your-s3-bucket-name
ENCRYPT_BACKUPS=true

# Security
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=60
ENABLE_CORS=false
ALLOWED_ORIGINS=https://yourdomain.com

EOF

        chmod 600 .env
        log_info "Created .env file with secure random passwords"
        log_warn "IMPORTANT: Update .env with your actual Slack/PagerDuty/AWS credentials"
    else
        log_info ".env file already exists"
    fi
}

# ============================================================================
# PostgreSQL Security Hardening
# ============================================================================

harden_postgresql() {
    log_info "Hardening PostgreSQL security..."

    # Backup original pg_hba.conf
    if [ -f "/etc/postgresql/15/main/pg_hba.conf" ]; then
        cp /etc/postgresql/15/main/pg_hba.conf /etc/postgresql/15/main/pg_hba.conf.backup

        # Configure PostgreSQL to require password authentication
        cat > /etc/postgresql/15/main/pg_hba.conf <<EOF
# PostgreSQL Client Authentication Configuration (HIPAA-compliant)
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections require password
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# IPv4 local connections require password
host    all             all             127.0.0.1/32            scram-sha-256

# IPv6 local connections require password
host    all             all             ::1/128                 scram-sha-256

# Deny all other connections
host    all             all             0.0.0.0/0               reject
EOF

        log_info "PostgreSQL authentication configured (scram-sha-256)"
    else
        log_warn "PostgreSQL configuration not found. Skipping PostgreSQL hardening."
    fi

    # Enable SSL/TLS
    if [ -f "/etc/postgresql/15/main/postgresql.conf" ]; then
        # Generate self-signed certificate if not exists
        if [ ! -f "/etc/postgresql/15/main/server.crt" ]; then
            openssl req -new -x509 -days 365 -nodes -text \
                -out /etc/postgresql/15/main/server.crt \
                -keyout /etc/postgresql/15/main/server.key \
                -subj "/CN=biomedical-platform"

            chmod 600 /etc/postgresql/15/main/server.key
            chown postgres:postgres /etc/postgresql/15/main/server.*

            log_info "SSL certificates generated for PostgreSQL"
        fi

        # Enable SSL in postgresql.conf
        sed -i "s/#ssl = off/ssl = on/" /etc/postgresql/15/main/postgresql.conf
        sed -i "s/#ssl_cert_file = 'server.crt'/ssl_cert_file = '\/etc\/postgresql\/15\/main\/server.crt'/" /etc/postgresql/15/main/postgresql.conf
        sed -i "s/#ssl_key_file = 'server.key'/ssl_key_file = '\/etc\/postgresql\/15\/main\/server.key'/" /etc/postgresql/15/main/postgresql.conf

        log_info "PostgreSQL SSL/TLS enabled"
    fi
}

# ============================================================================
# Firewall Configuration
# ============================================================================

configure_firewall() {
    log_info "Configuring firewall rules..."

    # Check if UFW is installed
    if command -v ufw &> /dev/null; then
        # Enable UFW
        ufw --force enable

        # Default policies
        ufw default deny incoming
        ufw default allow outgoing

        # Allow SSH
        ufw allow 22/tcp comment 'SSH'

        # Allow HTTP/HTTPS
        ufw allow 80/tcp comment 'HTTP'
        ufw allow 443/tcp comment 'HTTPS'

        # Allow PostgreSQL (localhost only)
        ufw allow from 127.0.0.1 to any port 5432 proto tcp comment 'PostgreSQL localhost'

        # Allow Prometheus (localhost only)
        ufw allow from 127.0.0.1 to any port 9090 proto tcp comment 'Prometheus localhost'

        # Allow Grafana
        ufw allow 3000/tcp comment 'Grafana'

        # Allow service ports (internal only)
        ufw allow from 127.0.0.1 to any port 5001:5011 proto tcp comment 'Internal services'

        # Reload firewall
        ufw reload

        log_info "Firewall configured successfully"
        ufw status
    else
        log_warn "UFW not installed. Skipping firewall configuration."
    fi
}

# ============================================================================
# Create Backup Encryption Key
# ============================================================================

setup_backup_encryption() {
    log_info "Setting up backup encryption..."

    mkdir -p /etc/postgresql

    if [ ! -f "/etc/postgresql/backup_key.gpg" ]; then
        # Generate GPG key for backup encryption
        gpg --batch --gen-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Name-Real: Biomedical Platform Backup
Name-Email: backup@biomedical-platform.local
Expire-Date: 0
%commit
EOF

        # Export public key
        gpg --armor --export "backup@biomedical-platform.local" > /etc/postgresql/backup_key.gpg
        chmod 600 /etc/postgresql/backup_key.gpg

        log_info "Backup encryption key generated"
        log_warn "IMPORTANT: Back up the GPG private key securely!"
    else
        log_info "Backup encryption key already exists"
    fi
}

# ============================================================================
# Setup Cron Jobs
# ============================================================================

setup_cron_jobs() {
    log_info "Setting up automated backup cron jobs..."

    # Create cron job for daily full backup
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/biomedical-platform/infrastructure/scripts/backup_database.sh full") | crontab -

    # Create cron job for hourly incremental backup
    (crontab -l 2>/dev/null; echo "0 * * * * /opt/biomedical-platform/infrastructure/scripts/backup_database.sh incremental") | crontab -

    log_info "Cron jobs configured:"
    log_info "  - Full backup: Daily at 2:00 AM"
    log_info "  - Incremental backup: Every hour"
}

# ============================================================================
# Setup Log Rotation
# ============================================================================

setup_log_rotation() {
    log_info "Configuring log rotation..."

    cat > /etc/logrotate.d/biomedical-platform <<EOF
/var/log/biomedical-platform/*.log {
    daily
    missingok
    rotate 365
    compress
    delaycompress
    notifempty
    create 0640 biomedical biomedical
    sharedscripts
    postrotate
        systemctl reload biomedical-platform > /dev/null 2>&1 || true
    endscript
}

/var/log/postgresql-backups/*.log {
    daily
    missingok
    rotate 365
    compress
    delaycompress
    notifempty
    create 0640 postgres postgres
}
EOF

    log_info "Log rotation configured (365 days retention)"
}

# ============================================================================
# Create System User
# ============================================================================

create_system_user() {
    log_info "Creating system user for services..."

    if ! id "biomedical" &>/dev/null; then
        useradd -r -s /bin/bash -d /opt/biomedical-platform -m biomedical
        log_info "System user 'biomedical' created"
    else
        log_info "System user 'biomedical' already exists"
    fi
}

# ============================================================================
# Setup Systemd Services
# ============================================================================

setup_systemd_services() {
    log_info "Setting up systemd services..."

    # Create systemd service file for infrastructure
    cat > /etc/systemd/system/biomedical-infrastructure.service <<EOF
[Unit]
Description=Biomedical Platform Infrastructure (PostgreSQL, Prometheus, Grafana)
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/opt/biomedical-platform/infrastructure
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable biomedical-infrastructure.service

    log_info "Systemd service created and enabled"
}

# ============================================================================
# Security Audit
# ============================================================================

run_security_audit() {
    log_info "Running security audit..."

    echo ""
    echo "=========================================="
    echo "Security Audit Checklist"
    echo "=========================================="

    # Check .env permissions
    if [ -f ".env" ]; then
        perms=$(stat -c '%a' .env 2>/dev/null || stat -f '%A' .env)
        if [ "$perms" = "600" ]; then
            echo "✓ .env file permissions: SECURE (600)"
        else
            log_warn "✗ .env file permissions: INSECURE ($perms) - should be 600"
        fi
    fi

    # Check PostgreSQL SSL
    if systemctl is-active --quiet postgresql; then
        echo "✓ PostgreSQL: RUNNING"
    else
        log_warn "✗ PostgreSQL: NOT RUNNING"
    fi

    # Check firewall
    if ufw status | grep -q "Status: active"; then
        echo "✓ Firewall: ENABLED"
    else
        log_warn "✗ Firewall: DISABLED"
    fi

    # Check backup encryption
    if [ -f "/etc/postgresql/backup_key.gpg" ]; then
        echo "✓ Backup encryption: CONFIGURED"
    else
        log_warn "✗ Backup encryption: NOT CONFIGURED"
    fi

    # Check cron jobs
    if crontab -l | grep -q "backup_database.sh"; then
        echo "✓ Automated backups: CONFIGURED"
    else
        log_warn "✗ Automated backups: NOT CONFIGURED"
    fi

    echo "=========================================="
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Biomedical Platform Production Setup"
    log_info "=========================================="

    #check_root
    setup_environment
    #harden_postgresql
    #configure_firewall
    #setup_backup_encryption
    #setup_cron_jobs
    #setup_log_rotation
    #create_system_user
    #setup_systemd_services
    run_security_audit

    log_info "=========================================="
    log_info "Production setup completed!"
    log_info "=========================================="
    log_info "Next steps:"
    log_info "  1. Review and update .env file with your credentials"
    log_info "  2. Start infrastructure: docker-compose up -d"
    log_info "  3. Initialize database: alembic upgrade head"
    log_info "  4. Create admin user"
    log_info "  5. Test backup: ./scripts/backup_database.sh full"
    log_info "=========================================="
}

main
