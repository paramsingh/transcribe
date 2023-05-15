import transcribe.db as db
from flask import g
import sqlite3
import pinecone
from gpt_index import GPTPineconeIndex
from transcribe.chat.insert_into_s2 import create_singlestore_connection


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


def get_s2_connection():
    s2_connection = getattr(g, "_s2_connection", None)
    if s2_connection is None:
        print("need to create s2 connection")
        s2_connection = g._s2_connection = create_singlestore_connection()
    else:
        print("using existing s2 connection")
    return s2_connection
