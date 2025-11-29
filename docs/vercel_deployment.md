# Deploying Django Ecommerce Backend to Vercel

## Overview

This guide explains how to deploy your Django ecommerce backend to Vercel's serverless platform. Since Vercel is optimized for serverless functions, we need external services for PostgreSQL and Redis.

## Important Considerations

### ⚠️ Limitations

1. **Serverless Architecture**: Each request runs in an isolated serverless function
2. **Cold Starts**: First request after inactivity may be slower (~1-3 seconds)
3. **No Persistent Storage**: Use external databases (cannot use SQLite)
4. **15MB Lambda Size**: Total deployment package must be under 15MB
5. **10-second Timeout**: Requests must complete within 10 seconds

### ✅ Best For

- APIs with external database connections
- Low to moderate traffic applications
- Prototypes and MVPs
- Cost-effective deployments (free tier available)

### ❌ Not Ideal For

- High-traffic production applications (consider Railway, Render, or AWS)
- Applications requiring WebSocket connections
- Long-running background tasks
- File uploads (need external storage like S3)

---

## Prerequisites

### 1. Vercel Account
- Sign up at [https://vercel.com](https://vercel.com)
- Install Vercel CLI: `npm install -g vercel`

### 2. External PostgreSQL Database
Choose one of these providers:

#### **Option A: Neon (Recommended - Free Tier)**
1. Sign up at [https://neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string (PostgreSQL connection string)
4. Format: `postgresql://user:password@host/database?sslmode=require`

#### **Option B: Supabase (Free Tier)**
1. Sign up at [https://supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database → Connection String
4. Copy the "Connection String" (URI format)

#### **Option C: Railway (Paid)**
1. Sign up at [https://railway.app](https://railway.app)
2. Create PostgreSQL database
3. Copy the DATABASE_URL from environment variables

#### **Option D: ElephantSQL (Free Tier)**
1. Sign up at [https://www.elephantsql.com](https://www.elephantsql.com)
2. Create a new instance (Tiny Turtle - Free)
3. Copy the URL from the details page

### 3. External Redis Cache
Choose one of these providers:

#### **Option A: Upstash (Recommended - Free Tier)**
1. Sign up at [https://upstash.com](https://upstash.com)
2. Create a Redis database
3. Copy the Redis URL from the details page
4. Format: `redis://default:password@endpoint:port`

#### **Option B: Redis Cloud (Free Tier)**
1. Sign up at [https://redis.com/try-free](https://redis.com/try-free)
2. Create a new database
3. Copy the public endpoint
4. Format: `redis://:password@endpoint:port`

#### **Option C: Railway (Paid)**
1. Create Redis instance on Railway
2. Copy the REDIS_URL from environment variables

---

## Deployment Steps

### Step 1: Prepare Your Project

1. **Ensure all files are committed**:
```bash
git add .
git commit -m "feat: prepare for Vercel deployment"
```

2. **Verify configuration files exist**:
```bash
ls -la vercel.json build.sh ecommerce/wsgi_vercel.py
```

### Step 2: Set Up Environment Variables

Create a `.env.production` file (don't commit this):

```env
# Django Settings
SECRET_KEY=your-production-secret-key-generate-new-one
DEBUG=False

# PostgreSQL Database (from Neon, Supabase, etc.)
DATABASE_URL=postgresql://user:password@host.region.provider.com/dbname?sslmode=require

# Redis Cache (from Upstash, Redis Cloud, etc.)
REDIS_URL=redis://default:password@endpoint.region.upstash.io:port

# Optional: Individual DB settings (Vercel will use DATABASE_URL if available)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your-db-host.provider.com
DB_PORT=5432
```

### Step 3: Deploy to Vercel

#### Method 1: Using Vercel CLI (Recommended)

1. **Login to Vercel**:
```bash
vercel login
```

2. **Deploy**:
```bash
vercel
```

3. **Follow prompts**:
   - Set up and deploy? **Y**
   - Which scope? **Select your account**
   - Link to existing project? **N**
   - Project name? **ecommerce-api** (or your choice)
   - Directory? **./  (current directory)**
   - Override settings? **N**

4. **Add environment variables**:
```bash
# Add each variable
vercel env add SECRET_KEY production
vercel env add DATABASE_URL production
vercel env add REDIS_URL production
vercel env add DEBUG production
```

5. **Deploy to production**:
```bash
vercel --prod
```

#### Method 2: Using GitHub Integration

1. **Push to GitHub**:
```bash
git remote add origin https://github.com/yourusername/ecommerce-backend.git
git push -u origin main
```

2. **Connect to Vercel**:
   - Go to [https://vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Configure project settings
   - Add environment variables in the dashboard

3. **Deploy**:
   - Vercel will automatically deploy on push to main branch

### Step 4: Run Database Migrations

After deployment, you need to run migrations:

#### Option A: Using Vercel CLI

Create a migration script `scripts/migrate.py`:
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.management import call_command

print("Running migrations...")
call_command('migrate')
print("Migrations completed!")
```

Run it:
```bash
vercel env pull .env.production
python scripts/migrate.py
```

#### Option B: Locally with Production Database

```bash
# Load production environment
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 5: Collect Static Files

Static files are collected during the build process via `build.sh`.

Verify in Vercel deployment logs:
```
✓ Collecting static files...
✓ Build completed successfully!
```

### Step 6: Test Your Deployment

1. **Get your deployment URL**:
```
https://your-project.vercel.app
```

2. **Test endpoints**:
```bash
# Homepage
curl https://your-project.vercel.app/

# API endpoints
curl https://your-project.vercel.app/api/categories/
curl https://your-project.vercel.app/api/products/

# Swagger docs
curl https://your-project.vercel.app/api/docs/
```

3. **Test authentication**:
```bash
# Register user
curl -X POST https://your-project.vercel.app/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login
curl -X POST https://your-project.vercel.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

---

## Environment Variables Reference

Add these to your Vercel project (Settings → Environment Variables):

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` (generate new!) |
| `DEBUG` | Debug mode | `False` (production) |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Redis connection | `redis://default:pass@host:port` |
| `ALLOWED_HOSTS` | Not needed (auto-configured) | - |

---

## Troubleshooting

### Issue: "No module named 'ecommerce'"
**Solution**: Ensure `vercel.json` points to correct WSGI file:
```json
"src": "ecommerce/wsgi.py"
```

### Issue: "Database connection failed"
**Solutions**:
1. Verify `DATABASE_URL` is correct and includes `?sslmode=require`
2. Check database is accessible from external connections
3. Ensure Neon/Supabase database is not paused (free tier limitation)

### Issue: "Redis connection timeout"
**Solutions**:
1. Verify `REDIS_URL` format is correct
2. Check Redis instance is running (Upstash has no sleep mode)
3. Ensure TLS/SSL is configured if required

### Issue: "502 Bad Gateway"
**Solutions**:
1. Check Vercel function logs: `vercel logs`
2. Reduce dependencies to stay under 15MB lambda size
3. Optimize imports and requirements.txt

### Issue: "Static files not loading"
**Solutions**:
1. Ensure `build.sh` runs `collectstatic`
2. Check `STATIC_ROOT` is set correctly
3. Verify `whitenoise` is in `INSTALLED_APPS`

### Issue: "Migrations not applied"
**Solution**: Run migrations manually (see Step 4)

---

## Performance Optimization for Vercel

### 1. Minimize Lambda Size

Remove unnecessary packages from `requirements.txt`:
```bash
# Only include what you need
pip freeze > requirements-full.txt
# Create minimal requirements.txt with only essentials
```

### 2. Use Caching Effectively

Vercel deployments benefit heavily from Redis caching:
- Cache database queries aggressively
- Use longer TTLs (Time To Live) for static data
- Implement cache warming for critical endpoints

### 3. Optimize Database Queries

- Use `select_related()` and `prefetch_related()`
- Add database indexes on frequently queried fields
- Limit query results with pagination

### 4. Configure Regions

Choose the region closest to your users:
```json
// vercel.json
{
  "regions": ["iad1"]  // US East (Northern Virginia)
  // or
  "regions": ["sfo1"]  // US West (San Francisco)
  // or
  "regions": ["fra1"]  // Europe (Frankfurt)
}
```

---

## Monitoring and Logs

### View Deployment Logs
```bash
vercel logs your-project-url
```

### Monitor Performance
1. Go to [https://vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. View Analytics tab for:
   - Request volume
   - Response times
   - Error rates
   - Geographic distribution

### Enable Error Tracking

Integrate Sentry for error tracking:
```bash
pip install sentry-sdk
```

Add to `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn="your-sentry-dsn",
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
    )
```

---

## Cost Estimation

### Vercel Pricing (as of 2025)

| Tier | Price | Limits |
|------|-------|--------|
| **Hobby** | Free | 100GB bandwidth, 100 serverless executions/day |
| **Pro** | $20/month | 1TB bandwidth, Unlimited executions |
| **Enterprise** | Custom | Custom limits, SLA support |

### External Services Pricing

**Neon (PostgreSQL)**:
- Free: 0.5GB storage, shared compute
- Paid: Starting at $19/month

**Upstash (Redis)**:
- Free: 10,000 commands/day, 256MB storage
- Paid: Pay-as-you-go, ~$0.40/100K commands

**Total Estimated Cost**:
- Free tier: $0/month (sufficient for testing)
- Production: ~$20-40/month

---

## Alternatives to Vercel for Django

If Vercel limitations are problematic, consider:

1. **Railway** - Better for Django, built-in PostgreSQL/Redis
   - Pricing: $5/month + usage
   - Deployment time: 2-3 minutes
   - No serverless limitations

2. **Render** - Native Django support
   - Pricing: Free tier available, $7/month for production
   - Managed PostgreSQL and Redis

3. **DigitalOcean App Platform**
   - Pricing: $5/month for basic apps
   - Full-featured PaaS

4. **AWS Elastic Beanstalk** - Enterprise solution
   - Pricing: Pay for AWS resources
   - More complex setup

5. **Google Cloud Run** - Container-based serverless
   - Pricing: Pay per request
   - Better for Django than Vercel

---

## Recommended: Use Railway Instead

For Django applications, **Railway** is often a better choice:

### Quick Railway Deployment

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Add PostgreSQL and Redis:
```bash
railway add postgresql
railway add redis
```

4. Railway auto-configures `DATABASE_URL` and `REDIS_URL` ✨

5. No cold starts, persistent connections, better Django support

---

## Summary

✅ **Vercel deployment is possible** but has limitations
✅ **Best for**: Low-traffic APIs, prototypes, MVPs
✅ **Requires**: External PostgreSQL (Neon) and Redis (Upstash)
✅ **Alternative**: Railway is often better for Django

Choose Vercel if:
- You need Vercel's global CDN
- You're already using Vercel for frontend
- You have low traffic requirements

Choose Railway/Render if:
- You need better Django support
- You want persistent connections
- You need background workers
- You prefer simpler deployment

---

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Neon PostgreSQL Docs](https://neon.tech/docs/introduction)
- [Upstash Redis Docs](https://docs.upstash.com/redis)
- [Railway Documentation](https://docs.railway.app/)