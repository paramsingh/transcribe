import json
import sqlite3

from transcribe.db.transcription import get_transcription_by_link
from typing import Optional


def get_embeddings_for_transcription(db: sqlite3.Connection, transcription_id: int) -> Optional[dict]:
    """ Gets an embedding by transcription. """
    cursor = db.cursor()
    cursor.execute(
        """
            SELECT id, transcription_id, embedding_json
              FROM embedding
             WHERE transcription_id = ?
        """,
        (transcription_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {
        'id': row[0],
        'transcription_id': row[1],
        'embedding_json': json.loads(row[2]),
    }


def get_embeddings_for_link(db: sqlite3.Connection, link: str) -> Optional[dict]:
    """ Gets an embedding by link. """
    transcription = get_transcription_by_link(db, link)
    if not transcription:
        return None
    return get_embeddings_for_transcription(db, transcription['id'])


def save_embeddings_for_link(db: sqlite3.Connection, link: str, embedding_json: str):
    transcription = get_transcription_by_link(db, link)
    if not transcription:
        raise Exception(f"Could not find transcription for link {link}")
    save_embeddings_for_transcription(db, transcription['id'], embedding_json)


def save_embeddings_for_transcription(db: sqlite3.Connection, transcription_id: int, embedding_json: str):
    """ Saves an embedding for a transcription. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO embedding (transcription_id, embedding_json)
             VALUES (?, ?)
        """,
        (transcription_id, embedding_json),
    )
    db.commit()


def create_embedding_request(db: sqlite3.Connection, transcription_id: int):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO embedding_request (transcription_id)
                VALUES (?)
        """,
        (transcription_id,),
    )
    db.commit()


def get_one_embedding_request(db: sqlite3.Connection) -> Optional[dict]:
    cursor = db.cursor()

    # get the first embedding request that doesn't have an embedding
    cursor.execute(
        """
            SELECT er.id, er.transcription_id, t.result
              FROM embedding_request er
              JOIN transcription t ON t.id = er.transcription_id
         LEFT JOIN embedding e ON e.transcription_id = er.transcription_id
             WHERE e.id IS NULL
          ORDER BY er.id
             LIMIT 1
        """
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {
        'id': row[0],
        'transcription_id': row[1],
        'result': row[2],
    }
