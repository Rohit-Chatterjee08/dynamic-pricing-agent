# Production-optimized multi-stage Dockerfile for Shopify Remix App
FROM node:18-alpine AS base

# Install system dependencies for native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    curl \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production --frozen-lockfile && npm cache clean --force

# Development stage
FROM base AS development
RUN npm ci --frozen-lockfile
COPY . .
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS build

# Copy all dependencies (including dev dependencies for build)
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Install curl for health checks
RUN apk add --no-cache curl

# Set working directory
WORKDIR /app

# Copy built application from build stage
COPY --from=build --chown=nextjs:nodejs /app/build ./build
COPY --from=build --chown=nextjs:nodejs /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/package.json ./package.json
COPY --from=build --chown=nextjs:nodejs /app/node_modules ./node_modules

# Copy Prisma schema and generated client
COPY --from=build --chown=nextjs:nodejs /app/prisma ./prisma

# Copy startup script
COPY --chown=nextjs:nodejs scripts/start.sh ./scripts/start.sh
RUN chmod +x ./scripts/start.sh

# Create directory for logs
RUN mkdir -p /app/logs && chown -R nextjs:nodejs /app/logs

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000/healthz || exit 1

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the application
CMD ["./scripts/start.sh"]
