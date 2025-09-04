-- Initialize PostgreSQL database for Shopify app production
-- This script ensures required extensions are available

-- Enable pgcrypto extension for UUID generation and encryption functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable pg_trgm for better text search performance (optional but recommended)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create a function to check if database is ready
CREATE OR REPLACE FUNCTION check_db_ready()
RETURNS boolean AS $$
BEGIN
  -- Simple check to ensure extensions are loaded
  RETURN (SELECT TRUE FROM pg_extension WHERE extname = 'pgcrypto');
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
  RAISE NOTICE 'Database initialized successfully for Shopify app production';
END $$;
