-- InscribeVerse Database Initialization Script
-- This script is run when the PostgreSQL container starts for the first time

-- Create additional databases for testing
CREATE DATABASE inscribeverse_test;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE inscribeverse_dev TO inscribeverse;
GRANT ALL PRIVILEGES ON DATABASE inscribeverse_test TO inscribeverse;

-- Enable extensions
\c inscribeverse_dev;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For JSON indexing

\c inscribeverse_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Log completion
\echo 'Database initialization completed successfully!' 