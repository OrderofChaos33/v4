# Deployment Guide

Guide for deploying the 280E MVP to production.

## Production Considerations

Before deploying to production:

1. ✅ Add database for persistent storage
2. ✅ Implement user authentication
3. ✅ Configure CORS properly
4. ✅ Set up HTTPS/SSL
5. ✅ Add rate limiting
6. ✅ Configure logging and monitoring
7. ✅ Set file size limits
8. ✅ Add error tracking (Sentry)
9. ✅ Configure backup strategy
10. ✅ Review security settings

## Environment Variables

Create a `.env` file:

```bash
# Application
APP_ENV=production
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Database (when implemented)
DATABASE_URL=postgresql://user:password@localhost/db_name

# File Upload
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=/var/data/uploads

# Security
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/280e/app.log

# Optional: External Services
OPENAI_API_KEY=your-openai-key  # For real LLM integration
SENTRY_DSN=your-sentry-dsn      # For error tracking
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "src.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/280e
    depends_on:
      - db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=280e
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

## Traditional Server Deployment

### Ubuntu/Debian Server

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nginx

# 3. Create application directory
sudo mkdir -p /var/www/280e
cd /var/www/280e

# 4. Clone repository
git clone https://github.com/OrderofChaos33/v4.git .

# 5. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt
pip install gunicorn

# 7. Create systemd service
sudo nano /etc/systemd/system/280e.service
```

### systemd Service File

```ini
[Unit]
Description=280E Expense Reclassification API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/280e
Environment="PATH=/var/www/280e/venv/bin"
ExecStart=/var/www/280e/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    src.api.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Enable service
sudo systemctl enable 280e

# Start service
sudo systemctl start 280e

# Check status
sudo systemctl status 280e

# View logs
sudo journalctl -u 280e -f
```

## Nginx Configuration

```nginx
upstream 280e_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location / {
        proxy_pass http://280e_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    location /docs {
        proxy_pass http://280e_api/docs;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://280e_api/health;
        access_log off;
    }
}
```

## Cloud Platforms

### AWS (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 280e-api

# Create environment
eb create 280e-production

# Deploy
eb deploy

# Open in browser
eb open
```

### Google Cloud (Cloud Run)

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/280e-api

# Deploy
gcloud run deploy 280e-api \
  --image gcr.io/PROJECT-ID/280e-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

```bash
# Create app
heroku create 280e-api

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open
heroku open
```

## Monitoring

### Health Check Endpoint

Monitor the `/health` endpoint:

```bash
curl https://api.yourdomain.com/health
```

### Logging

Configure structured logging:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/280e/app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Tools

- **Application Performance**: New Relic, DataDog
- **Error Tracking**: Sentry
- **Uptime Monitoring**: Pingdom, UptimeRobot
- **Log Aggregation**: ELK Stack, Splunk

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] CORS properly configured
- [ ] File upload validation and size limits
- [ ] Rate limiting configured
- [ ] Security headers set (HSTS, CSP, etc.)
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Backup strategy implemented

## Backup Strategy

```bash
# Database backup (when implemented)
pg_dump -h localhost -U user 280e > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /usr/local/bin/backup_280e.sh
```

## Scaling Considerations

1. **Horizontal Scaling**: Add more worker instances
2. **Database**: Use connection pooling
3. **Caching**: Add Redis for session/result caching
4. **CDN**: Use CloudFlare or AWS CloudFront
5. **Load Balancer**: Use AWS ELB or nginx load balancing

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u 280e -n 50

# Check port availability
sudo netstat -tulpn | grep 8000

# Test gunicorn directly
gunicorn src.api.main:app --bind 127.0.0.1:8000
```

### High Memory Usage

- Reduce number of workers
- Implement result caching
- Add database connection pooling
- Monitor for memory leaks

### Slow Performance

- Add caching layer
- Optimize database queries
- Increase worker timeout
- Use async processing for large files

## Support

For deployment issues:
1. Check logs: `sudo journalctl -u 280e -f`
2. Verify configuration files
3. Test endpoints with curl
4. Review nginx error logs: `/var/log/nginx/error.log`

## Production Checklist

Before going live:

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations complete
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backups tested
- [ ] Security review complete
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Support plan in place
