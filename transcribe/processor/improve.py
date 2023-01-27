"""A script to improve the transcriptions using GPT-3."""
from transcribe.config import OPENAI_API_KEY
from transcribe.db import init_db
from transcribe.db.transcription import (
    get_one_unimproved_transcription,
    add_improvement,
)
import openai
import json
import schedule
import time


class Improver:
    def __init__(self):
        self.db = init_db()

    def improve_one_transcription(self):
        """Get an unimproved transcription from the database and improve it."""

        unimproved = get_one_unimproved_transcription(self.db)
        print("improving transcription with link: ", unimproved["link"])
        result = json.loads(unimproved["result"])
        print("unimproved: ", result["transcription"])
        improved_text = self.improve_text(result["transcription"])
        add_improvement(self.db, improved_text, unimproved["uuid"])
        print("improved text:\n", improved_text)

    def improve_text(self, raw: str) -> str:
        words = raw.split()

        # create groups of 500 words to send to GPT-3
        word_groups = [words[i : i + 1000] for i in range(0, len(words), 1000)]
        print("Number of word groups: ", len(word_groups))
        print("Number of words: ", len(words))

        # TODO: add some validation to not improve long transcriptions, unless requested
        results = []

        for word_group in word_groups:

            text = " ".join(word_group)
            prompt = f"""Format the text from the transcript of a youtube video to add paragraphing, punctuations and capitalization. Also, remove any typos. Do NOT paraphrase or remove any sentences, only change the format and remove errors.

Transcript:

{text}

Improved transcript:
            """
            print(prompt)
            print("Making API call to GPT-3")
            # send text to GPT-3 and get back improved text
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                max_tokens=len(word_group) + 100,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
            )
            print("done")
            results.append(response.choices[0].text)
        return "\n".join(results)


if __name__ == "__main__":
    openai.api_key = OPENAI_API_KEY
    improver = Improver()
    schedule.every(1).minutes.do(improver.improve_one_transcription)
    while True:
        schedule.run_pending()
        time.sleep(1)
