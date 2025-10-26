# Production HTTPS Setup Guide

## Overview

This document provides instructions for enabling HTTPS in production to address the **Critical Security Vulnerability**: API accessible over unencrypted HTTP.

## Security Requirements

- ✅ All production traffic MUST use HTTPS (TLS 1.2 or higher)
- ✅ HTTP traffic should redirect to HTTPS
- ✅ Use trusted SSL/TLS certificates
- ✅ Implement HSTS (HTTP Strict Transport Security)
- ✅ Regular certificate renewal

## Option 1: Using Nginx Reverse Proxy (Recommended)

### Prerequisites
- Domain name pointed to your server
- Nginx installed
- Let's Encrypt (Certbot) for free SSL certificates

### Step 1: Install Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### Step 2: Configure Nginx

Create `/etc/nginx/sites-available/biomedical-platform`:

```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate paths (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API (Auth Dashboard Service)
    location /api {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 3: Obtain SSL Certificate

```bash
# Obtain and install certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 4: Enable and Start Nginx

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/biomedical-platform /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Option 2: Using Uvicorn with SSL

### For Development/Testing Only

```bash
# Generate self-signed certificate (DEV ONLY)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Run with SSL
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8100 \
  --ssl-keyfile=key.pem \
  --ssl-certfile=cert.pem
```

### For Production

```bash
# Use Let's Encrypt certificates
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8100 \
  --ssl-keyfile=/etc/letsencrypt/live/yourdomain.com/privkey.pem \
  --ssl-certfile=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
```

## Option 3: Using Cloud Provider Load Balancer

### AWS Application Load Balancer

1. **Create ACM Certificate**:
   - Go to AWS Certificate Manager
   - Request public certificate for your domain
   - Validate via DNS or email

2. **Configure ALB**:
   ```bash
   # Create target group
   aws elbv2 create-target-group \
     --name biomedical-platform-tg \
     --protocol HTTP \
     --port 8100 \
     --vpc-id vpc-xxxxx

   # Create load balancer with HTTPS listener
   aws elbv2 create-load-balancer \
     --name biomedical-platform-alb \
     --subnets subnet-xxxxx subnet-yyyyy \
     --security-groups sg-xxxxx

   # Add HTTPS listener
   aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:... \
     --protocol HTTPS \
     --port 443 \
     --certificates CertificateArn=arn:aws:acm:... \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
   ```

### Google Cloud Load Balancer

1. **Create SSL Certificate**:
   ```bash
   gcloud compute ssl-certificates create biomedical-platform-cert \
     --certificate=cert.pem \
     --private-key=key.pem
   ```

2. **Create HTTPS Load Balancer**:
   ```bash
   gcloud compute target-https-proxies create biomedical-platform-proxy \
     --url-map=biomedical-platform-map \
     --ssl-certificates=biomedical-platform-cert
   ```

## Post-Setup Verification

### 1. Test HTTPS Connection

```bash
# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test API endpoint
curl https://yourdomain.com/api/health
```

### 2. Verify Security Headers

```bash
curl -I https://yourdomain.com
# Should see:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
```

### 3. SSL Labs Test

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com

Target grade: **A or A+**

### 4. Update Frontend Configuration

Update frontend API base URL:

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://yourdomain.com/api';
```

## Automated Certificate Renewal

### Let's Encrypt (Certbot)

Certificates expire every 90 days. Set up automatic renewal:

```bash
# Add cron job
sudo crontab -e

# Add line:
0 0 * * * certbot renew --quiet && systemctl reload nginx
```

### Monitor Certificate Expiry

```bash
# Check expiry date
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

## Production Checklist

Before going live:

- [ ] SSL/TLS certificate installed and validated
- [ ] HTTP to HTTPS redirection working
- [ ] HSTS header configured
- [ ] Security headers present (X-Frame-Options, etc.)
- [ ] SSL Labs grade A or higher
- [ ] Auto-renewal configured and tested
- [ ] Frontend updated to use HTTPS API URL
- [ ] Database connections use SSL
- [ ] Monitoring alerts for certificate expiry
- [ ] Firewall rules updated (allow 443, block 80 or redirect only)

## Troubleshooting

### Certificate Not Found

```bash
# Check certificate location
sudo certbot certificates

# Renew if needed
sudo certbot renew
```

### Mixed Content Warnings

Ensure all resources (images, scripts, API calls) use HTTPS URLs.

### CORS Issues After HTTPS

Update CORS configuration to include HTTPS origin:

```python
# app/main.py
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## Security Score Impact

**Before HTTPS**:
- Security Score: 70/100
- Critical Vulnerabilities: 1 (HTTP not enforced)

**After HTTPS Setup**:
- Security Score: 95/100+ (expected)
- Critical Vulnerabilities: 0

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [OWASP Transport Layer Protection](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
