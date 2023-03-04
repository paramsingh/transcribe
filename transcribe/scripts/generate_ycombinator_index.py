import json
from transcribe.config import OPENAI_API_KEY
from transcribe.db import init_db
import transcribe.db.embedding as db_embedding
import transcribe.db.transcription as db_transcription
from typing import Optional
from gpt_index import GPTSimpleVectorIndex, GPTListIndex, Document, GPTPineconeIndex
import openai
import os
from yaspin import yaspin


import pinecone
api_key = "cab26ede-432b-40d5-bcf2-6f7849be9adc"
pinecone.init(api_key=api_key, environment="us-east1-gcp")
pindex = pinecone.Index("quickstart")


def get_ycombinator_videos():
    with open('ycombinator_videos.json') as f:
        data = json.load(f)
        return data


def get_link_from_id(id: str) -> str:
    return f'https://www.youtube.com/watch?v={id}'


def get_index_for_video(id: str, db) -> Optional[GPTSimpleVectorIndex]:
    link = get_link_from_id(id)
    embedding = db_embedding.get_embeddings_for_link(db, link)
    if not embedding:
        print("no embedding for link:", link)
        return None
    index = GPTSimpleVectorIndex.load_from_string(
        embedding['embedding_json'],
    )
    index.set_doc_id(link)
    summary = db_transcription.get_summary_for_link(db, link)
    if not summary:
        print("no summary for link:", link)
        return None
    index.set_text(summary)

    return index


def main(db):
    indexes = [get_index_for_video(video['id'], db)
               for video in get_ycombinator_videos()[:10]]
    indexes = [index for index in indexes if index is not None]
    big_index = GPTListIndex(indexes)
    question = input("question: ")
    with yaspin(text="thinking..."):
        response = big_index.query(question)
    print(response)
    print(response.get_formatted_sources())


if __name__ == '__main__':
    openai.api_key = OPENAI_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    db = init_db()
    main(db)
