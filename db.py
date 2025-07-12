import asyncpg
import os

DB_URL = os.getenv("DATABASE_URL")
pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DB_URL)

async def create_titles_table():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS titles (
                channel_id BIGINT PRIMARY KEY,
                title TEXT NOT NULL,
                curator_id BIGINT NOT NULL,
                translator_id BIGINT,
                editor_id BIGINT,
                cleaner_id BIGINT,
                typer_id BIGINT,
                beta_reader_id BIGINT
            )
        """)

async def insert_title(channel_id, title, curator_id):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO titles (channel_id, title, curator_id)
            VALUES ($1, $2, $3)
        """, channel_id, title, curator_id)

async def update_worker(channel_id, role_column, user_id):
    async with pool.acquire() as conn:
        await conn.execute(f"""
            UPDATE titles SET {role_column} = $1 WHERE channel_id = $2
        """, user_id, channel_id)

async def get_title(channel_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT * FROM titles WHERE channel_id = $1
        """, channel_id)
