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
        'embedding_json': row[2],
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
