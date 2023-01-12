from uuid import uuid4
from transcribe.db import init_db


def get_transcription(db, uuid: str) -> dict:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result FROM transcription WHERE uuid = ?;
    """,
        (uuid,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def get_transcription_by_link(db, link):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT uuid, link, result FROM transcription WHERE link = ?;
    """,
        (link,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def create_transcription(db, link: str, result: str) -> None:
    cursor = db.cursor()

    existing = get_transcription_by_link(db, link)
    if existing:
        return existing["uuid"]

    uuid = str(uuid4())
    cursor.execute(
        """
        INSERT INTO transcription (uuid, link, result) VALUES (?, ?, ?);
    """,
        (uuid, link, result),
    )
    db.commit()
    return uuid
