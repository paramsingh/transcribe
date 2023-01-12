from uuid import uuid4
from transcribe.db import init_db


def get_transcription(uuid: str) -> dict:
    connection = init_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM transcription WHERE uuid = ?;
    """,
        (uuid,),
    )
    result = cursor.fetchone()
    connection.close()

    if result:
        return {
            "uuid": result[0],
            "link": result[1],
            "result": result[2],
        }
    return None


def create_transcription(link: str, result: str) -> None:
    connection = init_db()
    cursor = connection.cursor()

    existing = get_transcription(link)
    if existing:
        return existing["uuid"]

    uuid = str(uuid4())
    cursor.execute(
        """
        INSERT INTO transcription (uuid, link, result) VALUES (?, ?, ?);
    """,
        (uuid, link, result),
    )
    connection.commit()
    connection.close()
    return uuid
