from uuid import uuid4
from transcribe.db import init_db


def transcription_exists(link):
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT EXISTS(SELECT 1 FROM transcription WHERE link = ? LIMIT 1);
    """,
        (link,),
    )
    exists = cursor.fetchone()[0]
    connection.close()
    return exists

def create_transcription(link: str, result: str) -> None:
    connection = init_db()
    cursor = connection.cursor()

    if transcription_exists(link):
        return None

    cursor.execute(
        """
        INSERT INTO transcription (uuid, link, result) VALUES (?, ?, ?);
    """,
        (str(uuid4()), link, result),
    )
    connection.commit()
    connection.close()
