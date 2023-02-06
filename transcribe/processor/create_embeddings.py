import json
import openai
import schedule
import time

from transcribe.chat.embeddings import generate_embeddings_for_transcription
from transcribe.config import OPENAI_API_KEY
from transcribe.db import init_db
from transcribe.db.embedding import get_one_embedding_request, save_embeddings_for_transcription


class EmbeddingCreator:
    def __init__(self):
        self.db = init_db()

    def process_one_embedding_request(self):
        request = get_one_embedding_request(self.db)
        if not request:
            print("nothing to do in this cycle!")
            return

        text = json.loads(request['result'])['transcription']
        embeddings = generate_embeddings_for_transcription(text)
        save_embeddings_for_transcription(
            self.db, request['transcription_id'], json.dumps(embeddings))


if __name__ == '__main__':
    openai.api_key = OPENAI_API_KEY

    schedule.every(1).minutes.do(
        EmbeddingCreator().process_one_embedding_request)
    while True:
        schedule.run_pending()
        time.sleep(1)
