import yt_dlp
import replicate
from transcribe.config import REPLICATE_API_KEY, DEVELOPMENT_MODE
from pathlib import Path
import json
from transcribe.db.transcription import (
    get_one_unfinished_transcription,
    populate_transcription,
    mark_transcription_failed
)
from transcribe.db import init_db
import schedule
import time

import sentry_sdk
from transcribe.processor import sentry_report
if not DEVELOPMENT_MODE:
    sentry_sdk.init(
        dsn="https://6e57fad284954d52957fa64eb14c80cb@o536026.ingest.sentry.io/4504604755427328",
        traces_sample_rate=1.0
    )


MAX_FILE_SIZE_TO_SEND_DIRECTLY = 30 * 1024 * 1024  # bytes
API_BASE_URL = "https://transcribe.param.codes/api/v1"


def get_downloaded_file_path(token: str) -> str:
    return f"/tmp/{token}.opus"


def get_file_size(file_path: str) -> int:
    return Path(file_path).stat().st_size


def get_api_endpoint(token: str) -> str:
    return f"{API_BASE_URL}/internal/transcription/{token}/file"


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
        token = unfinished["token"]

        print("Processing link for token: " + token + " with link: " + yt_link)
        try:
            self.download_video(yt_link, token)
        except Exception as e:
            print("Couldn't download video: ", e)
            sentry_report(e)
            mark_transcription_failed(self.db, token)
            return

        print("downloaded link for token: " + token)
        try:
            result = self.transcribe(token)
            populate_transcription(self.db, token, result)
            self.delete_downloaded_file(token)
            print(
                f"Done! Link: https://transcribe.param.codes/result/{token}"
            )
        except Exception as e:
            print("Transcription failed with error: ", e)
            sentry_report(e)
            mark_transcription_failed(self.db, token)
            return

    def delete_downloaded_file(self, token: str):
        path = get_downloaded_file_path(token)
        Path(path).unlink()

    def download_video(self, yt_link: str, token: str):
        """Use yt_dlp to download audio from a YT link to path"""
        path = get_downloaded_file_path(token)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": path,
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

    def transcribe(self, token: str) -> str:
        print("transcribing for token " + token)
        path = get_downloaded_file_path(token)
        if get_file_size(path) <= MAX_FILE_SIZE_TO_SEND_DIRECTLY:
            output = self.version.predict(audio=Path(f"/tmp/{token}.opus"))
        else:
            output = self.version.predict(audio=get_api_endpoint(token))
        print("done with transcription for " + token)
        return json.dumps(output)


if __name__ == "__main__":
    processor = WhisperProcessor()
    schedule.every(1).minutes.do(processor.process)
    while True:
        schedule.run_pending()
        time.sleep(1)
