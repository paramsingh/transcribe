import yt_dlp
import replicate
from pathlib import Path
import json
from transcribe.db.transcription import get_one_unfinished_transcription, populate_transcription
import schedule
import sqlite3
import time


class WhisperProcessor:
    def __init__(self):
        self.path = "/tmp/audio.opus"
        self.db = init_db()
        self.model = replicate.models.get("openai/whisper")
        self.version = self.model.versions.get("30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed")

    def process(self) -> None:
        unfinished = get_one_unfinished_transcription(self.db)
        if not unfinished:
            print("Nothing to do in this cycle!")
            return

        yt_link = unfinished["link"]
        uuid = unfinished["uuid"]
        self.download_video(yt_link)
        print("downloaded link for uuid: " + uuid)
        result = self.transcribe(uuid)
        populate_transcription(uuid, result)
        print("Done!")

    def download_video(self, yt_link: str):
        """Use yt_dlp to download audio from a YT link to path"""
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": self.path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "opus",
                    "preferredquality": "192",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_link])

    def transcribe(self, uuid) -> str:
        print("transcribing for uuid " + uuid)
        output = self.version.predict(audio=Path(self.path))
        print("done with transcription for " + uuid)
        return json.dumps(output)


def init_db() -> sqlite3.Connection:
    # TODO: this path needs to be a config option.
    connection = sqlite3.connect("database.db")
    return connection


if __name__ == '__main__':
    processor = WhisperProcessor()
    schedule.every(1).minutes.do(processor.process())
    while True:
        schedule.run_pending()
        time.sleep(1)
