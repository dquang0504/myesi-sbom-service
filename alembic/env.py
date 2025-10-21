# alembic/env.py
from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

# import Base metadata
from app.models.db import Base
target_metadata = Base.metadata

def run_migrations_online():
    config_section = config.get_section(config.config_ini_section)
    # override sqlalchemy.url from env var
    from app.core.config import Settings
    settings = Settings()
    config_section['sqlalchemy.url'] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        config_section,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_migrations)

    def do_migrations(connection: Connection):
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())

if context.is_offline_mode():
    raise RuntimeError("Offline mode not supported in this env.py")
else:
    run_migrations_online()
