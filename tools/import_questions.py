import json
import os
import sys

# Füge das übergeordnete Verzeichnis dem Pfad hinzu, um Module laden zu können
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importiere den QuizManager aus dem modules-Ordner
from modules.quiz_manager import QuizManager


def import_questions():
    """
    Liest Fragen aus einer JSON-Datei ein und importiert sie in die Datenbank.
    Bereits existierende Fragen werden aktualisiert.
    """
    # Öffne die JSON-Datei mit den Fragen
    with open('data/fragen.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    manager = QuizManager()
    conn = manager.get_connection()
    cur = conn.cursor()

    try:
        print(f"📚 Starte Import von {len(questions)} Fragen...")
        for question in questions:
            # Prüfe, ob die Frage bereits existiert
            cur.execute(
                """
                SELECT id FROM quiz_questions 
                WHERE frage = %s AND lernfeld = %s
            """, (question['frage'], question['lernfeld']))

            existing = cur.fetchone()

            if existing:
                # Wenn die Frage existiert → aktualisiere Punktezahl
                question_id = existing[0]
                print(f"🔄 Aktualisiere Frage: {question['frage'][:50]}...")
                cur.execute(
                    """
                    UPDATE quiz_questions 
                    SET punkte = %s
                    WHERE id = %s
                """, (question['punkte'], question_id))

                # Lösche alte Antworten zur Frage
                cur.execute("DELETE FROM quiz_answers WHERE question_id = %s",
                            (question_id, ))
            else:
                # Neue Frage einfügen
                print(f"➕ Neue Frage: {question['frage'][:50]}...")
                cur.execute(
                    """
                    INSERT INTO quiz_questions (frage, lernfeld, punkte)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (question['frage'], question['lernfeld'],
                      question['punkte']))
                question_id = cur.fetchone()[0]

            # Antworten zur Frage einfügen
            for i, answer in enumerate(question['antworten']):
                cur.execute(
                    """
                    INSERT INTO quiz_answers (question_id, antwort, is_correct)
                    VALUES (%s, %s, %s)
                """, (question_id, answer, i == question['richtig']))

        # Änderungen in der Datenbank speichern
        conn.commit()
        print("✅ Alle Fragen erfolgreich importiert/aktualisiert!")

    except Exception as e:
        # Im Fehlerfall alle Änderungen zurücksetzen
        conn.rollback()
        print(f"❌ Fehler beim Import: {e}")

    finally:
        # Verbindung ordnungsgemäß schließen
        cur.close()
        conn.close()


if __name__ == "__main__":
    import_questions()