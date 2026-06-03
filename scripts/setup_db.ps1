# scripts/setup_db.ps1
Write-Host "=== Database Setup Started ===" -ForegroundColor Green

# Load environment variables from .env file if exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
}

# Also set default values if not defined
$env:POSTGRES_USER = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "postgres" }
$env:POSTGRES_PASSWORD = if ($env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD } else { "733176" }
$env:POSTGRES_HOST = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "localhost" }
$env:POSTGRES_PORT = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }
$env:POSTGRES_DATABASE = if ($env:POSTGRES_DATABASE) { $env:POSTGRES_DATABASE } else { "employment_agency" }

# 1. Start main database
Write-Host "[1/5] Starting PostgreSQL container..." -ForegroundColor Yellow
docker compose up -d postgres

Write-Host "[2/5] Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Initialize Alembic
if (-not (Test-Path "alembic")) {
    Write-Host "[3/5] Initializing Alembic..." -ForegroundColor Yellow
    alembic init -t async alembic
} else {
    Write-Host "[3/5] Alembic already initialized, skipping..." -ForegroundColor Yellow
}

# Build the actual database URL for sync (for alembic.ini)
$databaseUrlSync = "postgresql+psycopg2://${env:POSTGRES_USER}:${env:POSTGRES_PASSWORD}@${env:POSTGRES_HOST}:${env:POSTGRES_PORT}/${env:POSTGRES_DATABASE}"
# For async operations
$databaseUrlAsync = "postgresql+asyncpg://${env:POSTGRES_USER}:${env:POSTGRES_PASSWORD}@${env:POSTGRES_HOST}:${env:POSTGRES_PORT}/${env:POSTGRES_DATABASE}"

Write-Host "Database URL: postgresql+psycopg2://${env:POSTGRES_USER}:***@${env:POSTGRES_HOST}:${env:POSTGRES_PORT}/${env:POSTGRES_DATABASE}" -ForegroundColor Gray

# 4. Configure alembic.ini with sync URL
Write-Host "[4/5] Configuring alembic.ini..." -ForegroundColor Yellow
$alembicIni = @"
[alembic]
script_location = alembic
version_locations = %(script_location)s/versions
sqlalchemy.url = ${databaseUrlSync}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"@
$alembicIni | Out-File -FilePath alembic.ini -Encoding ascii

# 5. Configure alembic/env.py for async
Write-Host "[5/5] Configuring alembic/env.py..." -ForegroundColor Yellow
$envPy = @'
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
from alembic import context

# Import metadata from your project
from src.dal.tables.base import metadata
from src.dal.tables.map import map_tables

# This is the Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        pass

# Map all tables
map_tables()
target_metadata = metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' async mode."""
    # Get the sync URL and convert to async
    sync_url = config.get_main_option("sqlalchemy.url")
    async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

    # Create async engine directly
    connectable = create_async_engine(
        async_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'@
$envPy | Out-File -FilePath alembic/env.py -Encoding utf8

Write-Host "Configuration completed!" -ForegroundColor Green

# 6. Generate initial migration
Write-Host "Generating initial migration..." -ForegroundColor Yellow

# Temporarily set sync URL for generation
alembic revision --autogenerate -m "initial migration"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration generated successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to generate migration!" -ForegroundColor Red
    exit 1
}

Write-Host "Applying migrations..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations applied successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to apply migrations!" -ForegroundColor Red
    exit 1
}

# 7. Seed initial data (NEW)
Write-Host "[7/5] Seeding initial database data..." -ForegroundColor Yellow
python ./scripts/seed_db.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database seeding completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Database Setup Completed Successfully! ===" -ForegroundColor Green
    Write-Host "You can now run the application."
} else {
    Write-Host "Failed to seed database!" -ForegroundColor Red
    exit 1
}