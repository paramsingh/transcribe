import singlestoredb as s2
import struct
import json
from transcribe.db import init_db
from transcribe.db.transcription import get_transcription_by_link
from transcribe.chat.chat import generate_embeddings_for_transcription
from transcribe.config import OPENAI_API_KEY
import openai
import tiktoken
import time

openai.api_key = OPENAI_API_KEY


def insert_embedding(conn, vector, txt, src=None):
    # Convert the array of floats to binary format
    binary_vector = struct.pack(f'{len(vector)}f', *vector)

    # Prepare the SQL query
    query = '''
        INSERT INTO embeddings (vector, text_data, src)
        VALUES (%s, %s, %s)
    '''

    # Execute the SQL query
    with conn.cursor() as cursor:
        cursor.execute(query, (binary_vector, txt, src))
        conn.commit()


def get_closest(conn, vector, limit=1):
    t = time.time()
    # Convert the array of floats to binary format
    binary_vector = struct.pack(f'{len(vector)}f', *vector)
    # print(binary_vector)

    # Prepare the SQL query
    query = '''
        SELECT text_data, src, DOT_PRODUCT(vector, %s) AS distance
        FROM embeddings
        ORDER BY distance DESC
        LIMIT %s
    '''

    # Execute the SQL query
    with conn.cursor() as cursor:
        cursor.execute(query, (binary_vector, limit))
        results = cursor.fetchall()
        print(f"took {time.time() - t} to get closest")
        return results


def embeddings_exist(conn, video_link):
    query = '''
        SELECT COUNT(*) AS count
        FROM embeddings
        WHERE src = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(query, (video_link,))
        result = cursor.fetchone()
        return result[0] > 0


def create_singlestore_connection():
    return s2.connect(
        host='svc-d996f713-3388-44fc-807f-97182ae2d360-dml.aws-oregon-4.svc.singlestore.com',
        port=3306,
        user='askyc_embeddings',
        database='askyc',
        password='gee-duster-bogey-moan',
    )


def get_context(conn, question: str) -> str:
    """ Gets a context for a question. """
    t = time.time()
    question_embedding = openai.Embedding.create(
        input=question,
        model="text-embedding-ada-002"
    )['data'][0]['embedding']
    print(f"took {time.time() - t} to get question embedding")
    # print("question_embedding", question_embedding)
    closest = get_closest(conn, question_embedding)
    # for c in closest:
    #     print(c[0])
    context = '\n'.join(c[0] for c in closest)
    return context, 'https://www.youtube.com/watch?v=' + closest[0][1]


def get_answer(conn, question: str):
    """ Gets an answer for a question. """
    t = time.time()
    context, source = get_context(conn, question)
    print(f"took {time.time() - t} to get context")
    prompt = f"""

You are a bot that answers questions about videos from YCombinator's YouTube channel. The context
will provide text from transcriptions of the channel. You should be as helpful as possible.

Answer the question based on the context below. Try to be detailed and explain things thoroughly.
If the question can't be answered based on the context,
say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:
"""
    t = time.time()
    response = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    print(f"took {time.time() - t} to get answer")
    return response["choices"][0].message["content"], source


def main():
    local_db = init_db()
    count = 0
    with create_singlestore_connection() as conn:
        with open('ycombinator_videos.json') as f:
            videos = json.load(f)
        for video in videos:
            link = 'https://www.youtube.com/watch?v=' + video['id']
            if embeddings_exist(conn, video['id']):
                print(f"Skipping {link}")
                continue
            transcription = get_transcription_by_link(
                local_db,
                link,
            )
            if transcription is not None and transcription['result'] is not None:
                result = json.loads(transcription['result'])
                embeddings = generate_embeddings_for_transcription(
                    result['transcription'],
                )
                groups = embeddings['groups']
                e = embeddings['embeddings']
                for group, embedding in zip(groups, e):
                    insert_embedding(conn, embedding, group, video['id'])
                print(len(groups), len(e), len(e[0]))
                count += 1
                print(f"{count} videos processed, {len(videos) - count} remain")


if __name__ == '__main__':
    openai.api_key = OPENAI_API_KEY
    # main()
    with create_singlestore_connection() as conn:
        t = time.time()
        print(get_answer(conn, "how do i start a startup"))
        print("Time taken:", time.time() - t)
        print(get_answer(conn, "how much money should I spend after my seed round"))
        print(get_answer(conn, "what should my primary KPIs be"))
