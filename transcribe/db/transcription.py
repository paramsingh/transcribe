from uuid import uuid4
from typing import Union, Optional, List, Dict
import sqlite3

RECENT_TRANSCRIPTION_COUNT = 5


def get_transcription_group(db, group_token: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, token, link FROM transcription WHERE token = ?;
    """,
        (group_token,),
    )
    parent = cursor.fetchone()
    if parent:
        cursor.execute(
            """
            SELECT token,
                   link,
                   CASE WHEN result IS NULL then 0 else 1 END,
                   transcribe_failed,
                   improvement_failed,
                   created
              FROM transcription WHERE id IN (
                SELECT transcription_id FROM transcription_group WHERE group_id = ?
              )
              ORDER BY created DESC
        """,
            (parent[0],)
        )
        children = cursor.fetchall()
        return {
            "id": parent[0],
            "group": {
                "token": parent[1],
                "link": parent[2],
                "members": {
                    "transcriptions": [{
                        "token": row[0],
                        "link": row[1],
                        "result_exists": bool(row[2]),
                        "transcribe_failed": row[3],
                        "improvement_failed": row[4],
                        "created": str(row[5]),
                    } for row in children]}
            }
        }
    return None


def get_transcription(db, token: str) -> Union[dict, None]:
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT token, link, result, improvement, summary, id
          FROM transcription WHERE token = ?;
    """,
        (token,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "token": result[0],
            "link": result[1],
            "result": result[2],
            "improvement": result[3],
            "summary": result[4],
            "id": result[5],
        }
    return None


def get_transcription_by_link(db, link):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT token, link, result, id, transcribe_failed
          FROM transcription
         WHERE link = ?;
    """,
        (link,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "token": result[0],
            "link": result[1],
            "result": result[2],
            "id": result[3],
            "transcribe_failed": bool(result[4]),
        }
    return None


def get_summary_for_link(db, link):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT summary
          FROM transcription
         WHERE link = ?;
    """,
        (link,),
    )
    result = cursor.fetchone()

    if result:
        return result[0]
    return None


def get_transcriptions_by_link(db, links: List[str]):
    cursor = db.cursor()
    placeholders = ", ".join("?" * len(links))
    cursor.execute(
        f"""
        SELECT token, link, id FROM transcription WHERE link in ({placeholders});
    """,
        links,
    )
    result = cursor.fetchall()

    if result:
        return {
            r[1]: (r[0], r[2])
            for r in result
        }
    return {}


def get_one_unfinished_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT token, link
          FROM transcription
         WHERE result is NULL
           AND transcribe_failed = 0
         LIMIT 1;
    """
    )
    result = cursor.fetchone()

    if result:
        return {"token": result[0], "link": result[1]}
    return None


def get_one_unimproved_transcription(db) -> Union[dict, None]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT t.token, t.link, t.result, t.improvement, t.summary, t.id, t.created
          FROM transcription t
     LEFT JOIN embedding e
            ON t.id = e.transcription_id
         WHERE (t.improvement is NULL OR t.summary IS NULL OR e.id IS NULL)
           AND t.result is NOT NULL
           AND t.improvement_failed = 0
           -- HUGE HACK: not improving old transcriptions
           -- TODO (param): eventually create embeddings for these
           -- and remove this hack
           AND CAST(strftime('%s', date(t.created)) as integer) > CAST(strftime('%s', '2023-02-16') as integer)
      ORDER BY t.created ASC
         LIMIT 1;
    """
    )
    result = cursor.fetchone()

    if result:
        return {
            "token": result[0],
            "link": result[1],
            "result": result[2],
            "improvement": result[3],
            "summary": result[4],
            "id": result[5],
            "created": result[6],
        }
    return None


def add_improvement(db, improved_text: str, token: str) -> None:
    """Add improved text to the improvement column for transcription with given token"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement = ? WHERE token = ?;
    """,
        (improved_text, token),
    )
    db.commit()


def mark_improvement_failed(db, token: str) -> None:
    """Mark transcription as failed improvement"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET improvement_failed = 1 WHERE token = ?;
    """,
        (token,),
    )
    db.commit()


def set_transcription_failed(db, token: str, value: bool) -> None:
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET transcribe_failed = ? WHERE token = ?;
    """,
        (1 if value else 0, token),
    )
    db.commit()


def add_summary(db, summary: str, token: str) -> None:
    """Add summary to the summary column for transcription with given token"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET summary = ? WHERE token = ?;
    """,
        (summary, token),
    )
    db.commit()


def populate_transcription(db, token: str, result: str) -> None:
    """Add result to a transcription"""
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transcription SET result = ? WHERE token = ?;
    """,
        (result, token),
    )
    db.commit()


def get_token_if_existing(db, link: str, user_id: int) -> Union[str, None]:
    existing = get_transcription_by_link(db, link)
    if existing:
        log_transcription_attempt(db, existing["id"], user_id)
        return existing["token"]
    return None


def get_ids_if_existing(db, links: List[str], user_id: int) -> Dict[str, str]:
    existing = get_transcriptions_by_link(db, links)
    if existing:
        for link, (token, _id) in existing.items():
            log_transcription_attempt(db, _id, user_id)
    return existing


def create_transcriptions_with_group(db, group_items: List[str], user_id: int, g_token: str, g_link: str):
    existing = get_ids_if_existing(db, group_items, user_id)
    c_ids = list([_id for (token, _id) in existing.values()])
    for link in group_items:
        if link not in existing:
            token = f"tr-{uuid4()}"
            c_id = create_transcription_with_token_returning_id(
                db, link, user_id, None, token)
            c_ids.append(c_id)
    g_id = create_transcription_with_token_returning_id(
        db, g_link, user_id, "GROUP_TRANSCRIPTION", g_token)
    create_group_entry(db, g_id, c_ids)


def create_group_entry(db, g_token, child_tokens):
    cursor = db.cursor()
    cursor.executemany(
        """
        INSERT INTO transcription_group (group_id, transcription_id) VALUES (?, ?)
        """,
        [(g_token, token) for token in child_tokens]
    )
    db.commit()


def create_transcription_with_transcription_token(db, link: str, user_id: int, result: Optional[str]) -> str:
    cursor = db.cursor()

    token = f"tr-{str(uuid4())}"
    cursor.execute(
        """
        INSERT INTO transcription (token, link, user_id, result) VALUES (?, ?, ?, ?);
    """,
        (token, link, user_id, result),
    )
    log_transcription_attempt(db, cursor.lastrowid, user_id)
    db.commit()
    return token


def create_transcription_with_token_returning_id(db, link: str, user_id: int, result: Union[None, str],
                                                 token: str) -> int:
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO transcription (token, link, user_id, result) VALUES (?, ?, ?, ?);
    """,
        (token, link, user_id, result),
    )
    log_transcription_attempt(db, cursor.lastrowid, user_id)
    db.commit()
    return cursor.lastrowid


def log_transcription_attempt(db: sqlite3.Connection, transcription_id: int, user_id: Optional[int]) -> None:
    if not user_id:
        return
    if not transcription_attempt_exists(db, transcription_id, user_id):
        add_transcription_attempt(db, transcription_id, user_id)


def add_transcription_attempt(db: sqlite3.Connection, transcription_id: int, user_id: int) -> None:
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO user_transcription_attempt (transcription_id, user_id)
             VALUES (?, ?);
    """,
        (transcription_id, user_id),
    )
    db.commit()


def transcription_attempt_exists(db: sqlite3.Connection, transcription_id: int, user_id: int) -> bool:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id
          FROM user_transcription_attempt
         WHERE transcription_id = ?
           AND user_id = ?;
    """,
        (transcription_id, user_id),
    )
    return cursor.fetchone() is not None


def get_user_transcription_attempts(db: sqlite3.Connection, user_id: int) -> int:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT t.token,
               t.link,
               CASE WHEN result IS NULL then 0 else 1 END,
               t.transcribe_failed,
               t.improvement_failed,
               ut.created
          FROM user_transcription_attempt ut
          JOIN transcription t
            ON t.id = ut.transcription_id
         WHERE ut.user_id = ?
      ORDER BY ut.created DESC;
        """,
        (user_id,),
    )
    return [{
        "token": row[0],
        "link": row[1],
        "result_exists": bool(row[2]),
        "transcribe_failed": row[3],
        "improvement_failed": row[4],
        "created": str(row[5]),
    } for row in cursor.fetchall()]


def get_recent_transcriptions(db: sqlite3.Connection, limit: int = RECENT_TRANSCRIPTION_COUNT) -> List[dict]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT token,
               link,
               CASE WHEN result IS NULL then 0 else 1 END,
               transcribe_failed,
               improvement_failed,
               created
          FROM transcription
         WHERE transcribe_failed = 0
      ORDER BY created DESC
         LIMIT ?
          """,
        (limit,)
    )

    return [{
        "token": row[0],
        "link": row[1],
        "result_exists": bool(row[2]),
        "transcribe_failed": row[3],
        "improvement_failed": row[4],
        "created": str(row[5]),
    } for row in cursor.fetchall()]


def count_unfinished_transcriptions(db: sqlite3.Connection) -> int:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT COUNT(*)
          FROM transcription
         WHERE result is NULL
           AND transcribe_failed = 0
    """
    )
    return cursor.fetchone()[0]
