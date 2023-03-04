import transcribe.db as db
from flask import g
import sqlite3
import pinecone
from gpt_index import GPTPineconeIndex


def get_flask_db() -> sqlite3.Connection:
    connection = getattr(g, "_database", None)
    if connection is None:
        connection = g._database = db.init_db()
    return connection


def get_pinecone_index() -> GPTPineconeIndex:
    pinecone_index = getattr(g, "_pinecone_index", None)
    if pinecone_index is None:
        pi = pinecone.Index("quickstart")
        pinecone_index = g._pinecone_index = GPTPineconeIndex.load_from_disk(
            'ycombinator_pinecone_index.json',
            pinecone_index=pi,
        )
    return pinecone_index
