import sqlite3


def get_transcriptions(db: sqlite3.Connection, limit: int = 1000, offset: int = 0) -> list:
    """ Gets all transcriptions. """
    cursor = db.cursor()
    cursor.execute(
        """
            SELECT token
              FROM transcription
             LIMIT ?
            OFFSET ?
        """,
        (limit, offset),
    )
    return [
        {
            "token": row[0],
        }
        for row in cursor.fetchall()
    ]


offset = 0
db = sqlite3.connect("database.db")
with open('frontend/public/sitemap.txt', 'w') as f:
    f.write("https://transcribe.param.codes\n")
    while True:
        transcriptions = get_transcriptions(db, offset=offset)
        if not transcriptions:
            break
        for t in transcriptions:
            print(f"https://transcribe.param.codes/result/{t['token']}")
            f.write(
                f"https://transcribe.param.codes/result/{t['token']}\n")
        for t in transcriptions:
            print(f"https://transcribe.param.codes/ask/{t['token']}")
            f.write(
                f"https://transcribe.param.codes/ask/{t['token']}\n")
        offset += 1000
