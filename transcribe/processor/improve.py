"""A script to improve the transcriptions using GPT-3."""
from typing import List
from transcribe.config import OPENAI_API_KEY
from transcribe.db import init_db
from transcribe.db.transcription import (
    get_one_unimproved_transcription,
    add_improvement,
    add_summary,
)
import openai
import json
import schedule
import time

WORD_GROUP_SIZE = 1000


class Improver:
    def __init__(self):
        self.db = init_db()

    def improve_one_transcription(self):
        """Get an unimproved transcription from the database and improve it."""

        unimproved = get_one_unimproved_transcription(self.db)
        if not unimproved:
            print("nothing to do in this cycle!")
            return
        print("improving transcription with link: ", unimproved["link"])
        result = json.loads(unimproved["result"])
        if not unimproved["improvement"]:
            print("Improving...")
            improved_text = self.improve_text(result["transcription"])
            add_improvement(self.db, improved_text, unimproved["uuid"])
            print("Done improving!")
        else:
            print("improvement already exists, skipping improvement step")

        if not unimproved["summary"]:
            print("Summarizing...")
            summary = self.summarize_text(result["transcription"])
            add_summary(self.db, summary, unimproved["uuid"])
            print("Done summarizing!")
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

    def make_openai_request(self, prompt: str, max_tokens: int) -> str:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )
        return response.choices[0].text

    def group_and_make_openai_requests(self, raw: str, prompt: str) -> str:
        word_groups = self.get_word_groups(raw)
        results = []
        for word_group in word_groups:
            text = " ".join(word_group)
            result = self.make_openai_request(
                prompt.format(text=text), len(word_group) + 500)
            results.append(result)
        return "\n".join(results)

    def improve_text(self, raw: str) -> str:

        # TODO: add some validation to not improve long transcriptions, unless requested
        prompt = """Format the text from the transcript of a youtube video to add paragraphing, punctuations and capitalization. Also, remove any typos. Do NOT paraphrase or remove any sentences, only change the format and remove errors.

Transcript:
{text}

Improved transcript:"""
        return self.group_and_make_openai_requests(raw, prompt)

    def summarize_text(self, raw: str) -> str:
        """ Create a summary of the text using GPT-3 """
        prompt = """Summarize the following text in nested bullet point format. Make sure to capture all the important ideas in the text.
Text:
{text}

Summary:"""
        return self.group_and_make_openai_requests(raw, prompt)


if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY
    improver = Improver()
    schedule.every(1).minutes.do(improver.improve_one_transcription)
    while True:
        schedule.run_pending()
        time.sleep(1)
