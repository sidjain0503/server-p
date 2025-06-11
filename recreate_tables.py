#!/usr/bin/env python3
"""
Script to drop and recreate database tables for meta-engine schemas.
This ensures all new columns (like SaaS subscription fields) are properly added.
"""

import asyncio
from app.core.database import db_manager
from app.meta_engine.orchestrator import get_meta_engine
from app.models.schemas.registry import register_all_schemas


async def recreate_meta_tables():
    """Drop and recreate all database tables for registered meta-engine schemas."""
    print("🗑️  Dropping and recreating meta-engine database tables...")
    
    # Connect to database
    await db_manager.connect()
    
    # Register all schemas first
    register_all_schemas()
    
    # Get meta-engine
    meta_engine = get_meta_engine()
    
    print(f"📋 Found {len(meta_engine.list_schemas())} schemas to recreate tables for")
    
    # Drop and create tables for each registered schema
    async with db_manager.engine.begin() as conn:
        # First, drop all existing tables
        print("🗑️  Dropping existing tables...")
        for schema_name in meta_engine.list_schemas():
            model = meta_engine.get_model(schema_name)
            if model:
                try:
                    print(f"   🗑️  Dropping table for {schema_name}: {model.__tablename__}")
                    await conn.run_sync(model.metadata.drop_all)
                except Exception as e:
                    print(f"   ⚠️  Could not drop {schema_name} (may not exist): {e}")
        
        # Then, create all tables with new schema
        print("🔨 Creating tables with updated schema...")
        for schema_name in meta_engine.list_schemas():
            model = meta_engine.get_model(schema_name)
            if model:
                print(f"   ✅ Creating table for {schema_name}: {model.__tablename__}")
                await conn.run_sync(model.metadata.create_all)
            else:
                print(f"   ❌ No model found for schema: {schema_name}")
    
    print("✅ All meta-engine tables recreated successfully with updated schema!")
    
    # Close connection
    await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(recreate_meta_tables()) 