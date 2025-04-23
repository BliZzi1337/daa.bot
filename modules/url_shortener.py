import string
import random
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from modules.db_setup import get_db_connection

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return code.lower()

class URLShortener:
    def __init__(self):
        try:
            self.setup_table()
        except Exception as e:
            print(f"❌ URL-Kürzer-Initialisierung fehlgeschlagen: {str(e)}")
            raise

    def setup_table(self):
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute('DROP INDEX IF EXISTS shortened_urls_short_code_idx')
            cur.execute('DROP INDEX IF EXISTS shortened_urls_long_url_idx')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS shortened_urls (
                    id SERIAL PRIMARY KEY,
                    short_code TEXT UNIQUE NOT NULL,
                    long_url TEXT NOT NULL,
                    user_id BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('CREATE INDEX IF NOT EXISTS shortened_urls_short_code_idx ON shortened_urls(short_code)')
            cur.execute('CREATE INDEX IF NOT EXISTS shortened_urls_long_url_idx ON shortened_urls(long_url)')

            conn.commit()
        finally:
            cur.close()
            conn.close()

    def create_short_url(self, long_url, user_id, custom_code=None):
        if not long_url:
            raise ValueError("URL darf nicht leer sein")

        conn = get_db_connection()
        cur = None
        try:
            cur = conn.cursor()

            if custom_code:
                cur.execute('SELECT id FROM shortened_urls WHERE short_code = %s', (custom_code,))
                if cur.fetchone():
                    raise ValueError("Dieser Code ist bereits vergeben")

                cur.execute('''
                    INSERT INTO shortened_urls (short_code, long_url, user_id) 
                    VALUES (%s, %s, %s) 
                    RETURNING short_code
                ''', (custom_code, long_url, user_id))
                conn.commit()
                return custom_code

            cur.execute('SELECT short_code FROM shortened_urls WHERE long_url = %s', (long_url,))
            existing = cur.fetchone()
            if existing:
                return existing[0]

            max_attempts = 10
            base_length = 6

            for attempt in range(max_attempts):
                length = base_length + attempt
                short_code = generate_short_code(length=length)

                try:
                    cur.execute('''
                        INSERT INTO shortened_urls (short_code, long_url, user_id) 
                        VALUES (%s, %s, %s) 
                        ON CONFLICT (short_code) DO NOTHING 
                        RETURNING short_code
                    ''', (short_code, long_url, user_id))
                    conn.commit()

                    result = cur.fetchone()
                    if result:
                        return result[0]
                except psycopg2.Error:
                    if cur and not cur.closed:
                        conn.rollback()
                    continue

            raise Exception("Konnte keinen eindeutigen Code generieren. Bitte erneut versuchen.")

        except Exception as e:
            raise
        finally:
            if cur and not cur.closed:
                cur.close()
            if conn:
                conn.close()

    def get_long_url(self, short_code):
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT long_url FROM shortened_urls WHERE short_code = %s', (short_code,))
            result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            raise
        finally:
            if conn:
                conn.close()

async def setup(bot):
    pass