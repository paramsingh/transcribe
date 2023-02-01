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


MAX_FILE_SIZE_TO_SEND_DIRECTLY = 80 * 1024 * 1024  # bytes
API_BASE_URL = "https://transcribe.param.codes/api/v1"


def get_downloaded_file_path(uuid: str) -> str:
    return f"/tmp/{uuid}.opus"


def get_file_size(file_path: str) -> int:
    return Path(file_path).stat().st_size


def get_api_endpoint(uuid: str) -> str:
    return f"{API_BASE_URL}/internal/transcription/{uuid}/file"


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
        try:
            result = self.transcribe(uuid)
            populate_transcription(self.db, uuid, result)
            self.delete_downloaded_file(uuid)
            print(
                f"Done! Link: https://transcribe.param.codes/result/{uuid}"
            )
        except Exception as e:
            print("Transcription failed with error: ", e)
            sentry_report(e)
            mark_transcription_failed(self.db, uuid)
            return

    def delete_downloaded_file(self, uuid):
        path = get_downloaded_file_path(uuid)
        Path(path).unlink()

    def download_video(self, yt_link: str, uuid: str):
        """Use yt_dlp to download audio from a YT link to path"""
        path = get_downloaded_file_path(uuid)
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

    def transcribe(self, uuid) -> str:
        print("transcribing for uuid " + uuid)
        path = get_downloaded_file_path(uuid)
        if get_file_size(path) <= MAX_FILE_SIZE_TO_SEND_DIRECTLY:
            output = self.version.predict(audio=Path(f"/tmp/{uuid}.opus"))
        else:
            output = self.version.predict(audio=get_api_endpoint(uuid))
        print("done with transcription for " + uuid)
        return json.dumps(output)


if __name__ == "__main__":
    processor = WhisperProcessor()
    schedule.every(1).minutes.do(processor.process)
    while True:
        schedule.run_pending()
        time.sleep(1)
