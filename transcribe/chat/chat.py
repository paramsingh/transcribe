import json
import openai
import transcribe.config as config
import tiktoken

from transcribe.db import init_db

user_id = 1  # me@param.codes
KARPATHY_VIDEO_LINK = "https://www.youtube.com/watch?v=kCc8FmEb1nY"

tokenizer = tiktoken.encoding_for_model("text-davinci-003")
MAX_TOKENS = 1500
MAX_PROMPT_TOKENS = 1800


def group_sentences(text: str):
    """ Groups sentences into groups of MAX_TOKENS tokens. """
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    groups = []
    count = 0
    current_group = []
    for sentence in sentences:
        tokens = tokenizer.encode(sentence)
        if count + len(tokens) > MAX_TOKENS:
            count = 0
            groups.append(". ".join(current_group) + ". ")
            current_group = []

        if len(tokens) > MAX_TOKENS:
            continue

        current_group.append(sentence)
        count += len(tokens)

    if current_group:
        groups.append(". ".join(current_group) + ". ")
    return groups


def generate_embeddings_for_transcription(text: str):
    """ Gets OpenAI embeddings for a transcription, for semantic search. """
    groups = group_sentences(text)
    embeddings = []
    for group in groups:
        embedding = openai.Embedding.create(
            input=group,
            model="text-embedding-ada-002"
        )
        vector = embedding['data'][0]['embedding']
        embeddings.append(vector)
    return {"groups": groups, "embeddings": embeddings}
