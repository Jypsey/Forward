import psycopg2
from psycopg2.extras import RealDictCursor
import os

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="telegram_forwarderok",
            user=os.getenv("DB_USER", "adish"),
            password=os.getenv("DB_PASSWORD", "Sughesh"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS media_queue (
                    id SERIAL PRIMARY KEY,
                    file_path TEXT,
                    caption TEXT,
                    is_video BOOLEAN,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()

    def add_media(self, file_path, caption, is_video):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO media_queue (file_path, caption, is_video)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (file_path, caption, is_video))
            self.conn.commit()
            return cur.fetchone()[0]

    def get_pending_media(self, limit=5):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM media_queue 
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            """, (limit,))
            return cur.fetchall()

    def mark_completed(self, media_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE media_queue SET status = 'completed'
                WHERE id = %s
            """, (media_id,))
            self.conn.commit()

    def cleanup_old(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM media_queue
                WHERE status = 'completed' AND created_at < NOW() - INTERVAL '1 hour'
            """)
            self.conn.commit()
