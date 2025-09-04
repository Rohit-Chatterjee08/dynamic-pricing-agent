-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- CreateEnum
CREATE TYPE "subscription_status" AS ENUM ('ACTIVE', 'CANCELLED', 'EXPIRED', 'TRIAL', 'PENDING', 'FROZEN');

-- CreateEnum
CREATE TYPE "billing_status" AS ENUM ('PENDING', 'PAID', 'FAILED', 'REFUNDED');

-- CreateEnum
CREATE TYPE "webhook_status" AS ENUM ('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED', 'RETRY');

-- CreateEnum
CREATE TYPE "job_status" AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED');

-- CreateTable
CREATE TABLE "sessions" (
    "id" TEXT NOT NULL,
    "shop" TEXT NOT NULL,
    "state" TEXT NOT NULL,
    "isOnline" BOOLEAN NOT NULL DEFAULT false,
    "scope" TEXT,
    "expires" TIMESTAMP(3),
    "access_token" TEXT NOT NULL,
    "user_id" BIGINT,
    "first_name" TEXT,
    "last_name" TEXT,
    "email" TEXT,
    "account_owner" BOOLEAN NOT NULL DEFAULT false,
    "locale" TEXT,
    "collaborator" BOOLEAN DEFAULT false,
    "email_verified" BOOLEAN DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "shops" (
    "id" TEXT NOT NULL,
    "shop" TEXT NOT NULL,
    "name" TEXT,
    "email" TEXT,
    "domain" TEXT,
    "province" TEXT,
    "country" TEXT,
    "address1" TEXT,
    "zip" TEXT,
    "city" TEXT,
    "phone" TEXT,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "primary_locale" TEXT,
    "address2" TEXT,
    "installed_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "uninstalled_at" TIMESTAMP(3),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "plan_name" TEXT,
    "access_token_encrypted" TEXT,
    "webhook_secret" TEXT,
    "app_settings" JSONB,
    "features" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "shops_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "subscriptions" (
    "id" TEXT NOT NULL,
    "shop" TEXT NOT NULL,
    "shopify_subscription_id" TEXT,
    "name" TEXT NOT NULL,
    "status" "subscription_status" NOT NULL,
    "current_period_end" TIMESTAMP(3),
    "trial_days" INTEGER,
    "trial_ends_on" TIMESTAMP(3),
    "price" DECIMAL(10,2) NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'USD',
    "capped_amount" DECIMAL(10,2),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "subscriptions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "billing_cycles" (
    "id" TEXT NOT NULL,
    "shop" TEXT NOT NULL,
    "subscription_id" TEXT NOT NULL,
    "start_date" TIMESTAMP(3) NOT NULL,
    "end_date" TIMESTAMP(3) NOT NULL,
    "amount" DECIMAL(10,2) NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'USD',
    "status" "billing_status" NOT NULL DEFAULT 'PENDING',
    "shopify_charge_id" TEXT,
    "billed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "billing_cycles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "usage_records" (
    "id" TEXT NOT NULL,
    "subscription_id" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "price" DECIMAL(10,2) NOT NULL,
    "recorded_at" TIMESTAMP(3) NOT NULL,
    "shopify_usage_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "usage_records_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "webhook_deliveries" (
    "id" TEXT NOT NULL,
    "shop" TEXT NOT NULL,
    "topic" TEXT NOT NULL,
    "webhook_id" TEXT,
    "headers" JSONB,
    "body" JSONB,
    "query_params" JSONB,
    "status" "webhook_status" NOT NULL DEFAULT 'PENDING',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "last_attempt_at" TIMESTAMP(3),
    "processed_at" TIMESTAMP(3),
    "error_message" TEXT,
    "hmac_valid" BOOLEAN,
    "job_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "webhook_deliveries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "queue_jobs" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "data" JSONB NOT NULL,
    "status" "job_status" NOT NULL DEFAULT 'PENDING',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "max_attempts" INTEGER NOT NULL DEFAULT 3,
    "scheduled_for" TIMESTAMP(3),
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "failed_at" TIMESTAMP(3),
    "error_message" TEXT,
    "error_stack" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "queue_jobs_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "sessions_shop_idx" ON "sessions"("shop");

-- CreateIndex
CREATE INDEX "sessions_expires_idx" ON "sessions"("expires");

-- CreateIndex
CREATE UNIQUE INDEX "shops_shop_key" ON "shops"("shop");

-- CreateIndex
CREATE INDEX "shops_shop_idx" ON "shops"("shop");

-- CreateIndex
CREATE INDEX "shops_is_active_idx" ON "shops"("is_active");

-- CreateIndex
CREATE INDEX "shops_installed_at_idx" ON "shops"("installed_at");

-- CreateIndex
CREATE UNIQUE INDEX "subscriptions_shopify_subscription_id_key" ON "subscriptions"("shopify_subscription_id");

-- CreateIndex
CREATE INDEX "subscriptions_shop_idx" ON "subscriptions"("shop");

-- CreateIndex
CREATE INDEX "subscriptions_status_idx" ON "subscriptions"("status");

-- CreateIndex
CREATE INDEX "subscriptions_current_period_end_idx" ON "subscriptions"("current_period_end");

-- CreateIndex
CREATE INDEX "billing_cycles_shop_idx" ON "billing_cycles"("shop");

-- CreateIndex
CREATE INDEX "billing_cycles_status_idx" ON "billing_cycles"("status");

-- CreateIndex
CREATE INDEX "billing_cycles_start_date_end_date_idx" ON "billing_cycles"("start_date", "end_date");

-- CreateIndex
CREATE UNIQUE INDEX "usage_records_shopify_usage_id_key" ON "usage_records"("shopify_usage_id");

-- CreateIndex
CREATE INDEX "usage_records_subscription_id_idx" ON "usage_records"("subscription_id");

-- CreateIndex
CREATE INDEX "usage_records_recorded_at_idx" ON "usage_records"("recorded_at");

-- CreateIndex
CREATE INDEX "webhook_deliveries_shop_topic_idx" ON "webhook_deliveries"("shop", "topic");

-- CreateIndex
CREATE INDEX "webhook_deliveries_status_idx" ON "webhook_deliveries"("status");

-- CreateIndex
CREATE INDEX "webhook_deliveries_created_at_idx" ON "webhook_deliveries"("created_at");

-- CreateIndex
CREATE INDEX "queue_jobs_status_scheduled_for_idx" ON "queue_jobs"("status", "scheduled_for");

-- CreateIndex
CREATE INDEX "queue_jobs_type_idx" ON "queue_jobs"("type");

-- CreateIndex
CREATE INDEX "queue_jobs_created_at_idx" ON "queue_jobs"("created_at");

-- AddForeignKey
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_shop_fkey" FOREIGN KEY ("shop") REFERENCES "shops"("shop") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "subscriptions" ADD CONSTRAINT "subscriptions_shop_fkey" FOREIGN KEY ("shop") REFERENCES "shops"("shop") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "billing_cycles" ADD CONSTRAINT "billing_cycles_shop_fkey" FOREIGN KEY ("shop") REFERENCES "shops"("shop") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "billing_cycles" ADD CONSTRAINT "billing_cycles_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "subscriptions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "usage_records" ADD CONSTRAINT "usage_records_subscription_id_fkey" FOREIGN KEY ("subscription_id") REFERENCES "subscriptions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "webhook_deliveries" ADD CONSTRAINT "webhook_deliveries_shop_fkey" FOREIGN KEY ("shop") REFERENCES "shops"("shop") ON DELETE CASCADE ON UPDATE CASCADE;
