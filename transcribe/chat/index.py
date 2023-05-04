from gpt_index import GPTSimpleVectorIndex, Document
import os
from transcribe.config import OPENAI_API_KEY
from transcribe.db import init_db
import transcribe.db.transcription as transcription_db
import transcribe.db.embedding as embedding_db

KARPATHY_LINKS = [
    'https://www.youtube.com/watch?v=VMj-3S1tku0',
    'https://www.youtube.com/watch?v=PaCmpygFfXo',
    'https://www.youtube.com/watch?v=TCH_1BHY58I',
    'https://www.youtube.com/watch?v=P6sfmUTpUmc',
    'https://www.youtube.com/watch?v=q8SA3rM6ckI',
    'https://www.youtube.com/watch?v=t3YJ5hKiMQ0',
    'https://www.youtube.com/watch?v=kCc8FmEb1nY',
]


if __name__ == '__main__':
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    db = init_db()
    link = input("Enter a link: ")
    embeddings = embedding_db.get_embeddings_for_link(db, link)
    index = GPTSimpleVectorIndex.load_from_string(embeddings['embedding_json'])
    question = input("Ask a question: ")
    print(index.query(question))
