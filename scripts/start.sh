#!/bin/bash

# Production startup script for Shopify Remix App
set -e  # Exit on any error

echo "🚀 Starting Shopify App Production Server..."

# Environment validation
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "❌ ERROR: REDIS_URL is not set"
    exit 1
fi

if [ -z "$SHOPIFY_API_KEY" ]; then
    echo "❌ ERROR: SHOPIFY_API_KEY is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
until npx prisma db execute --stdin < <(echo "SELECT 1;") >/dev/null 2>&1; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done
echo "✅ Database connection established"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis connection..."
until redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; do
    echo "Redis not ready, waiting 5 seconds..."
    sleep 5
done
echo "✅ Redis connection established"

# Run database migrations
echo "📦 Running database migrations..."
npx prisma migrate deploy
echo "✅ Database migrations completed"

# Generate Prisma client
echo "🔧 Generating Prisma client..."
npx prisma generate
echo "✅ Prisma client generated"

# Create log directory if it doesn't exist
mkdir -p /app/logs

# Start the application with proper logging
echo "🌟 Starting application server..."
exec node build/server/index.js
