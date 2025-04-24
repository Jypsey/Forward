import psycopg2
from psycopg2 import sql

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="telegram_forwarder",
            user="postgres",
            password="yourpassword",
            host="localhost",
            port="5432"
        )
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS media_queue (
                    id SERIAL PRIMARY KEY,
                    file_id TEXT,
                    file_path TEXT,
                    caption TEXT,
                    is_video BOOLEAN,
                    source_message_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()

    async def add_media(self, file_id, file_path, caption, is_video, source_message_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO media_queue 
                (file_id, file_path, caption, is_video, source_message_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (file_id, file_path, caption, is_video, source_message_id))
            self.conn.commit()
            return cur.fetchone()[0]

    async def get_pending_media(self, limit=5):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, file_path, caption, is_video 
                FROM media_queue 
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            """, (limit,))
            return cur.fetchall()

    async def mark_completed(self, media_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE media_queue 
                SET status = 'completed' 
                WHERE id = %s
            """, (media_id,))
            self.conn.commit()

    async def cleanup_completed(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM media_queue 
                WHERE status = 'completed' 
                AND created_at < NOW() - INTERVAL '1 hour'
            """)
            self.conn.commit()
            return cur.rowcount
