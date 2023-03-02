"""A script to improve the transcriptions using GPT-3."""
from typing import List
from transcribe.config import OPENAI_API_KEY, DEVELOPMENT_MODE
from transcribe.db import init_db
from transcribe.db.transcription import (
    get_one_unimproved_transcription,
    add_improvement,
    add_summary,
    mark_improvement_failed
)
import transcribe.db.embedding as db_embedding
import os
import openai
import json
import schedule
import time
import sentry_sdk
from transcribe.processor import sentry_report
from gpt_index import Document, GPTSimpleVectorIndex
from yaspin import yaspin

if not DEVELOPMENT_MODE:
    sentry_sdk.init(
        dsn="https://6e57fad284954d52957fa64eb14c80cb@o536026.ingest.sentry.io/4504604755427328",
        traces_sample_rate=1.0
    )

WORD_GROUP_SIZE = 1000

DAVINCI_MAX_TOKENS = 4097


class Improver:
    def __init__(self):
        self.db = init_db()

    def get_token_count(self, messages: List[dict]) -> int:
        size = sum([len(message["content"].split()) for message in messages])
        return size // 4

    def improve_one_transcription(self):
        """Get an unimproved transcription from the database and improve it."""

        unimproved = get_one_unimproved_transcription(self.db)
        if not unimproved:
            print("nothing to do in this cycle!")
            return
        print("improving transcription with link: ", unimproved["link"])
        try:
            result = json.loads(unimproved["result"])
        except Exception as e:
            sentry_report(e)
            print("Improvement failed with error: ", e)
            mark_improvement_failed(self.db, unimproved["token"])
            return

        if not unimproved["improvement"]:
            print("Improving...")
            try:
                with yaspin(text="Summarizing...", timer=True):
                    improved_text = self.improve_text(result["transcription"])
                add_improvement(self.db, improved_text, unimproved["token"])
                print("Done improving!")
            except Exception as e:
                sentry_report(e)
                print("Improvement failed with error: ", e)
                mark_improvement_failed(self.db, unimproved["token"])
                return
        else:
            print("improvement already exists, skipping improvement step")

        if not unimproved["summary"]:
            print("Summarizing...")
            try:
                with yaspin(text="Summarizing...", timer=True):
                    summary = self.summarize_text(result["transcription"])
                add_summary(self.db, summary, unimproved["token"])
                print("Done summarizing!")
            except Exception as e:
                sentry_report(e)
                print("Summarization failed with error: ", e)
                mark_improvement_failed(self.db, unimproved["token"])
                return

        print("Creating index...")
        try:
            embedding = db_embedding.get_embeddings_for_transcription(
                self.db, unimproved["id"])
            if not embedding:
                with yaspin(text="Summarizing...", timer=True):
                    embedding = self.create_embeddings(
                        unimproved["result"], unimproved["link"])
                db_embedding.save_embeddings_for_transcription(
                    self.db, unimproved["id"], embedding)
            print("Done creating index!")
        except Exception as e:
            sentry_report(e)
            print("Index creation failed with error: ", e)
            mark_improvement_failed(self.db, unimproved["token"])
            return

        print("Done improving transcription with link: ", unimproved["link"])

    def get_word_groups(self, raw: str) -> List[str]:
        words = raw.split()

        # create groups of words to send to GPT-3
        word_groups = [
            words[i: i + WORD_GROUP_SIZE]
            for i in range(0, len(words), WORD_GROUP_SIZE)
        ]
        print("Number of word groups: ", len(word_groups))
        print("Number of words: ", len(words))
        return word_groups

    def make_openai_request(self, messages: List[dict], max_tokens: int) -> str:
        prompt_size = self.get_token_count(messages)
        if max_tokens + prompt_size > DAVINCI_MAX_TOKENS:
            max_tokens = DAVINCI_MAX_TOKENS - prompt_size
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0]["message"]["content"]

    def group_and_make_openai_requests(self, raw: str, system_input: dict) -> str:
        word_groups = self.get_word_groups(raw)
        results = []
        for word_group in word_groups:
            text = " ".join(word_group)
            messages = [
                system_input,
                {"role": "user", "content": text},
            ]
            result = self.make_openai_request(
                [system_input, {"role": "user", "content": text}], self.get_token_count(messages) + 100)
            results.append(result)
        return "\n".join(results)

    def improve_text(self, raw: str) -> str:

        # TODO: add some validation to not improve long transcriptions, unless requested
        system_input = {
            "role": "system",
            "content":  """Format the text from the transcript of a youtube video (provided by the user) to add paragraphing, punctuations and capitalization. Also, remove any typos. Do NOT paraphrase or remove any sentences, only change the format and remove errors.""",
        }

        return self.group_and_make_openai_requests(raw, system_input)

    def summarize_text(self, raw: str) -> str:
        """ Create a summary of the text using GPT-3 """
        system_input = {
            "role": "system", "content": "Summarize the transcription of a Youtube video the user provides succinctly in a few paragraphs. Make sure to capture all the important ideas in the text. The summary should be succinct and to the point."}
        return self.group_and_make_openai_requests(raw, system_input)

    def create_embeddings(self, raw: str, link: str) -> str:
        """ Create embeddings for the text using GPT-3 """
        text = f"""
The following is the transcription of a youtube video (Link: {link}).

{raw}"""
        document = Document(text)
        index = GPTSimpleVectorIndex([document])
        return index.save_to_string()


if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    improver = Improver()
    schedule.every(10).seconds.do(improver.improve_one_transcription)
    while True:
        schedule.run_pending()
        time.sleep(1)
