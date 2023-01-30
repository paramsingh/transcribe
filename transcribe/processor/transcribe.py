import yt_dlp
import replicate
from transcribe.config import REPLICATE_API_KEY
from pathlib import Path
import json
from transcribe.db.transcription import (
    get_one_unfinished_transcription,
    populate_transcription,
)
from transcribe.db import init_db
import schedule
import time


class WhisperProcessor:
    def __init__(self):
        self.db = init_db()
        client = replicate.Client(api_token=REPLICATE_API_KEY)
        self.model = client.models.get("openai/whisper")
        self.version = self.model.versions.get(
            "30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed"
        )

    def process(self) -> None:
        unfinished = get_one_unfinished_transcription(self.db)
        if not unfinished:
            print("Nothing to do in this cycle!")
            return

        yt_link = unfinished["link"]
        uuid = unfinished["uuid"]
        print("Processing link for uuid: " + uuid + " with link: " + yt_link)
        self.download_video(yt_link, uuid)
        print("downloaded link for uuid: " + uuid)
        result = self.transcribe(uuid)
        populate_transcription(self.db, uuid, result)
        print(
            f"Done! Link: https://transcribe.param.codes/api/v1/transcription/{uuid}/details"
        )

    def download_video(self, yt_link: str, uuid: str):
        """Use yt_dlp to download audio from a YT link to path"""
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"/tmp/{uuid}.opus",
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
        output = self.version.predict(audio=Path(f"/tmp/{uuid}.opus"))
        print("done with transcription for " + uuid)
        return json.dumps(output)


if __name__ == "__main__":
    processor = WhisperProcessor()
    schedule.every(1).minutes.do(processor.process)
    while True:
        schedule.run_pending()
        time.sleep(1)
