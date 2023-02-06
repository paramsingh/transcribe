import json
import openai

from transcribe.config import OPENAI_API_KEY
from transcribe.chat.embeddings import generate_embeddings_for_transcription, get_answer
from transcribe.db.transcription import get_transcription_by_link
from transcribe.db.embedding import get_embeddings_for_transcription, save_embeddings_for_transcription
from transcribe.db import init_db


def main():
    db = init_db()
    link = input("Enter a link to a video: ")
    transcription = get_transcription_by_link(db, link)
    if not transcription or not transcription['result']:
        print("We do not have a transcription for this link, please submit it to transcribe.param.codes")
        return

    question = input("Enter a question: ")
    embeddings = get_embeddings_for_transcription(db, transcription['id'])
    if not embeddings:
        print("No embeddings in the database, generating them now...")
        embeddings = generate_embeddings_for_transcription(
            json.loads(transcription['result'])['transcription'])
        save_embeddings_for_transcription(
            db, transcription['id'], json.dumps(embeddings))
        print("Done!")
    else:
        embeddings = embeddings['embedding_json']

    print("Have embeddings!")
    print(get_answer(question, embeddings))


if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY
    main()
