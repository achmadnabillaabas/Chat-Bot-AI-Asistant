# Deployment Guide

## Production Deployment

### Prerequisites
- PostgreSQL 14+ database instance
- Qdrant vector database (Docker or cloud)
- 9Router API key
- Node.js 18+ runtime
- Python 3.11+ runtime
- Domain with SSL certificate

---

## Backend Deployment

### 1. Environment Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set production environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export NINEROUTER_API_KEY="your-production-key"
export JWT_SECRET="generate-strong-random-secret"
export QDRANT_URL="https://your-qdrant-instance"
export TELEGRAM_BOT_TOKEN="your-bot-token"
```

### 2. Database Migration

```bash
# Run migrations
alembic upgrade head

# Create initial admin user (create script in Phase 9)
python scripts/create_admin.py
```

### 3. Run with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 4. Docker Deployment (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ai_assistant
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/ai_assistant
      QDRANT_URL: http://qdrant:6333
      NINEROUTER_API_KEY: ${NINEROUTER_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - qdrant

volumes:
  postgres_data:
  qdrant_data:
```

---

## Frontend Deployment

### 1. Build for Production

```bash
cd frontend
npm run build
```

### 2. Environment Variables

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### 3. Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 4. Deploy to Custom Server

```bash
# Build the app
npm run build

# Start production server
npm start
```

### 5. Docker Deployment

**Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

---

## Nginx Configuration

```nginx
# Backend API
upstream backend {
    server localhost:8000;
}

# Frontend
upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend;
    }
}
```

---

## Security Checklist

### Environment
- [ ] Use strong JWT_SECRET (32+ random characters)
- [ ] Enable HTTPS/SSL
- [ ] Set proper CORS_ORIGINS
- [ ] Restrict database access to backend only
- [ ] Use environment variables, never hardcode secrets

### Database
- [ ] Use strong database password
- [ ] Enable SSL connection to database
- [ ] Regular backups configured
- [ ] Limit database user permissions

### API
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using SQLAlchemy ORM)
- [ ] File upload size limits enforced
- [ ] File type validation

### Telegram
- [ ] Verify webhook requests
- [ ] Whitelist allowed user IDs
- [ ] Secure bot token

---

## Monitoring

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Readiness check
curl https://api.yourdomain.com/api/health/ready
```

### Logging

**Backend:**
- Use structured logging (JSON format)
- Log levels: INFO for normal, ERROR for failures
- Log rotation configured

**Frontend:**
- Client-side error tracking (Sentry, etc.)
- Performance monitoring

### Metrics to Monitor

- API response time
- 9Router latency
- Database query time
- Qdrant search latency
- Token usage per day
- Error rates
- Active users
- Conversation count

---

## Backup Strategy

### Database Backup

```bash
# Automated daily backup
pg_dump -U user -h host ai_assistant > backup_$(date +%Y%m%d).sql

# Restore
psql -U user -h host ai_assistant < backup_20240101.sql
```

### Qdrant Backup

```bash
# Backup Qdrant collections
docker exec qdrant_container tar czf /tmp/qdrant_backup.tar.gz /qdrant/storage

# Copy from container
docker cp qdrant_container:/tmp/qdrant_backup.tar.gz ./
```

### Document Storage Backup

```bash
# Backup uploaded files
tar czf documents_backup_$(date +%Y%m%d).tar.gz /path/to/uploads
```

---

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Run multiple backend instances
- Session storage in Redis (for Phase 9+)
- CDN for frontend static assets

### Database Scaling
- Read replicas for analytics queries
- Connection pooling (already configured in SQLAlchemy)
- Regular VACUUM and ANALYZE

### Qdrant Scaling
- Qdrant cluster for large datasets
- Separate collections per knowledge base

---

## Rollback Procedure

### Backend Rollback

```bash
# Revert to previous migration
alembic downgrade -1

# Deploy previous backend version
git checkout <previous-tag>
pip install -r requirements.txt
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend Rollback

```bash
# Vercel automatic rollback
vercel rollback

# Manual rollback
git checkout <previous-tag>
npm ci
npm run build
npm start
```

---

## Post-Deployment Verification

1. [ ] Health endpoints respond
2. [ ] Can create new user account
3. [ ] Can start new conversation
4. [ ] 9Router integration working
5. [ ] Token usage being recorded
6. [ ] Document upload working (Phase 6+)
7. [ ] RAG retrieval working (Phase 7+)
8. [ ] Telegram bot responding (Phase 5+)
9. [ ] Analytics page loading
10. [ ] All navigation links working

---

## Troubleshooting

### Backend not starting
- Check environment variables
- Verify database connection
- Check logs: `docker logs backend`

### Frontend not loading
- Check API_URL configuration
- Verify CORS settings
- Check browser console for errors

### 9Router errors
- Verify API key is valid
- Check 9Router status page
- Review rate limits

### Database migration errors
- Backup database first
- Check Alembic version
- Manually verify schema

---

## Performance Optimization

### Backend
- Enable SQLAlchemy query caching
- Use connection pooling
- Implement Redis caching for frequent queries
- Index database columns appropriately

### Frontend
- Enable Next.js ISR (Incremental Static Regeneration)
- Optimize images with Next.js Image component
- Lazy load heavy components
- Code splitting for routes

### Qdrant
- Tune HNSW parameters for speed vs accuracy
- Use quantization for large datasets
- Implement result caching
