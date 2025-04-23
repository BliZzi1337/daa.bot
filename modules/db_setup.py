import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.pool import SimpleConnectionPool

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Initialisiere den Connection-Pool
pool = None

def get_db_connection():
    """
    Stelle eine Verbindung zur Datenbank her (mit Connection Pooling).
    """
    global pool
    if pool is None:
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL ist nicht gesetzt")

            # Erstelle einen Connection-Pool mit bis zu 20 Verbindungen
            pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                dsn=database_url,
                connect_timeout=3
            )

            # Teste die Verbindung
            test_conn = pool.getconn()
            test_conn.close()
            pool.putconn(test_conn)

        except KeyError:
            print("❌ DEBUG: DATABASE_URL wurde nicht in den Umgebungsvariablen gefunden")
            raise ValueError("Die Umgebungsvariable DATABASE_URL fehlt")
        except Exception as e:
            print(f"❌ DEBUG: Fehler bei der Datenbankverbindung: {str(e)}")
            print(f"FEHLER: Verbindung zur Datenbank fehlgeschlagen: {e}")
            raise
    return pool.getconn()

def setup_database():
    """
    Erstellt notwendige Tabellen für das Quiz- und URL-Shortening-System.
    """
    database_url = os.environ['DATABASE_URL']

    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Tabelle für Quiz-Fragen
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id SERIAL PRIMARY KEY,
            frage TEXT NOT NULL,
            lernfeld VARCHAR(10) NOT NULL,
            punkte INTEGER NOT NULL
        )
    """)

    # Tabelle für mögliche Antworten zu den Quiz-Fragen
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id SERIAL PRIMARY KEY,
            question_id INTEGER REFERENCES quiz_questions(id),
            antwort TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL
        )
    """)

    # Tabelle zur Speicherung des Fortschritts pro Nutzer und Lernfeld
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_progress (
            user_id BIGINT NOT NULL,
            lernfeld VARCHAR(10) NOT NULL,
            gesamt INTEGER DEFAULT 0,
            richtig INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, lernfeld)
        )
    """)

    # Tabelle für URL-Shortener zurücksetzen und neu erstellen
    cur.execute("DROP TABLE IF EXISTS shortened_urls")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shortened_urls (
            id SERIAL PRIMARY KEY,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            user_id BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.close()
    conn.close()

async def setup(bot):
    """
    Asynchrone Setup-Funktion für den Discord-Bot.
    Initialisiert die Datenbank.
    """
    setup_database()