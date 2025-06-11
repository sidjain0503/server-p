#!/usr/bin/env python3
"""
Temporary script to create database tables for meta-engine schemas.
This should be integrated into the database initialization process.
"""

import asyncio
from app.core.database import db_manager
from app.meta_engine.orchestrator import get_meta_engine
from app.models.schemas.registry import register_all_schemas


async def create_meta_tables():
    """Create all database tables for registered meta-engine schemas."""
    print("🏗️  Creating meta-engine database tables...")
    
    # Connect to database
    await db_manager.connect()
    
    # Register all schemas first
    register_all_schemas()
    
    # Get meta-engine
    meta_engine = get_meta_engine()
    
    print(f"📋 Found {len(meta_engine.list_schemas())} schemas to create tables for")
    
    # Create tables for each registered schema
    async with db_manager.engine.begin() as conn:
        for schema_name in meta_engine.list_schemas():
            model = meta_engine.get_model(schema_name)
            if model:
                print(f"   🔨 Creating table for {schema_name}: {model.__tablename__}")
                await conn.run_sync(model.metadata.create_all)
            else:
                print(f"   ❌ No model found for schema: {schema_name}")
    
    print("✅ All meta-engine tables created successfully!")
    
    # Close connection
    await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(create_meta_tables()) 