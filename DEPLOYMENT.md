# Deployment Guide for Render

This guide will walk you through deploying your Nalewka application on Render.

## Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Python Knowledge**: Basic understanding of Python and Flask

## Method 1: Manual Deployment

### Step 1: Create a Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: `nalewka-app`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT nalewka:app`

### Step 2: Add Environment Variables

In your web service settings, add these environment variables:

- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a secure random string (you can use an online generator)
- `DATABASE_URL`: Will be set automatically when you add a database

### Step 3: Add PostgreSQL Database

1. In your Render dashboard, click "New +" and select "PostgreSQL"
2. Configure the database:
   - **Name**: `nalewka-db`
   - **Database**: `nalewka`
   - **User**: `nalewka_user`
   - **Region**: Same as your web service
3. Copy the connection string to your web service's `DATABASE_URL` environment variable

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the build to complete (usually 2-5 minutes)

## Method 2: Using render.yaml (Recommended)

### Step 1: Push Your Code

Make sure your repository includes the `render.yaml` file:

```yaml
services:
  - type: web
    name: nalewka-app
    env: python
    buildCommand: bash build.sh
    startCommand: gunicorn --bind 0.0.0.0:$PORT nalewka:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: nalewka-db
          property: connectionString

databases:
  - name: nalewka-db
    databaseName: nalewka
    user: nalewka_user
```

### Step 2: Create Blueprint

1. In Render dashboard, click "New +" and select "Blueprint"
2. Connect your repository
3. Render will automatically create both the web service and database

## Database Migrations and Data Preservation

The deployment process has been designed to handle database migrations while preserving existing data:

1. **Automatic Migrations**: The `deploy.py` script automatically runs database migrations using Flask-Migrate
2. **Data Preservation**: Existing data is preserved during deployments
3. **Smart Sample Data Creation**: Sample data is only created if no users exist in the database

## Post-Deployment Setup

### Initialize Database with Sample Data

After deployment, you can optionally initialize the database with sample data:

1. **Option A: Using Render Shell**
   - Go to your web service in Render dashboard
   - Click "Shell" tab
   - Run: `python deploy.py --sample`

2. **Option B: Force Sample Data Creation**
   - If you want to recreate sample data even when users exist:
   - Run: `python deploy.py --force-sample`

### Verify Deployment

1. Visit your application URL (provided by Render)
2. You should see the Nalewka homepage
3. If you created sample data, try logging in with:
   - Username: `admin`
   - Password: `password123`

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment | Yes | `production` |
| `SECRET_KEY` | Secret key for sessions | Yes | Auto-generated |
| `DATABASE_URL` | PostgreSQL connection string | Yes | Auto-set by Render |
| `MAIL_USERNAME` | SMTP username for email notifications | No | Empty |
| `MAIL_PASSWORD` | SMTP password for email notifications | No | Empty |
| `ADMIN_EMAIL` | Admin email for notifications | No | `admin@example.com` |
| `RECAPTCHA_PUBLIC_KEY` | Google reCAPTCHA public key | No | Empty |
| `RECAPTCHA_PRIVATE_KEY` | Google reCAPTCHA private key | No | Empty |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No | Empty |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | No | Empty |
| `PYTHON_VERSION` | Python version | No | `3.10.0` |

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **Database Connection Issues**
   - Ensure `DATABASE_URL` is set correctly
   - Check that database is in the same region as web service
   - Verify database is running

3. **Application Crashes**
   - Check application logs in Render dashboard
   - Verify all environment variables are set
   - Ensure database is initialized

### Logs and Debugging

- **Build Logs**: Available in the "Logs" tab of your web service
- **Application Logs**: Available in the "Logs" tab after deployment
- **Database Logs**: Available in the database service dashboard

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **Database Access**: Use connection pooling and secure connections
3. **HTTPS**: Render automatically provides HTTPS for your application
4. **Secrets**: Use Render's secret management for sensitive data

## Scaling

### Free Tier Limitations

- **Web Services**: 750 hours/month
- **Databases**: 90 days free trial
- **Bandwidth**: 100GB/month

### Upgrading

To upgrade from free tier:
1. Go to your service settings
2. Click "Upgrade"
3. Choose your plan
4. Update your billing information

## Monitoring

### Health Checks

Render automatically monitors your application:
- **Health Check URL**: `/` (your homepage)
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds

### Custom Monitoring

You can add custom health checks by:
1. Creating a `/health` endpoint in your Flask app
2. Setting the health check URL in your service settings

## Backup and Recovery

### Database Backups

Render automatically backs up PostgreSQL databases:
- **Backup Frequency**: Daily
- **Retention**: 7 days (free tier)
- **Manual Backups**: Available in database dashboard

### Application Backups

- **Code**: Stored in your Git repository
- **Configuration**: Stored in Render dashboard
- **Environment Variables**: Stored securely in Render

## Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Community Forum**: [community.render.com](https://community.render.com)
- **Email Support**: Available for paid plans

## Cost Estimation

### Free Tier
- **Web Service**: Free (750 hours/month)
- **Database**: Free trial (90 days)
- **Total**: $0/month (with limitations)

### Paid Plans
- **Web Service**: $7/month (unlimited)
- **Database**: $7/month (unlimited)
- **Total**: ~$14/month (unlimited usage)
