import json
import openai
from openai.embeddings_utils import distances_from_embeddings
import transcribe.config as config
import tiktoken

from transcribe.db import init_db

from transcribe.db.transcription import get_user_transcription_attempts, get_transcription_by_link
import numpy

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


def get_context(question: str, data: dict) -> str:
    """ Gets a context for a question. """
    embeddings = data['embeddings']
    groups = data['groups']
    question_embedding = openai.Embedding.create(
        input=question,
        model="text-embedding-ada-002"
    )['data'][0]['embedding']
    distances = distances_from_embeddings(
        question_embedding,
        embeddings,
        distance_metric="cosine",
    )
    sorted_indices = numpy.argsort(distances)

    current_prompt = []
    token_count = 0
    for i in sorted_indices:
        tokens = tokenizer.encode(groups[i])
        if token_count + len(tokens) > MAX_PROMPT_TOKENS:
            break
        token_count += len(tokens)
        current_prompt.append(groups[i])

    return "\n\n".join(current_prompt)


def get_answer(question: str, embeddings: dict) -> str:
    """ Gets an answer for a question. """
    context = get_context(question, embeddings)
    response = openai.Completion.create(
        prompt=f"""
Answer the question based on the context below,
and if the question can't be answered based on the context,
say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:
""",
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        max_tokens=150,
        model="text-davinci-003",
    )
    return response["choices"][0]["text"].strip()
