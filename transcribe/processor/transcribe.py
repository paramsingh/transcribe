import yt_dlp
import replicate
from transcribe.config import REPLICATE_API_KEY, DEVELOPMENT_MODE
from pathlib import Path
import json
from transcribe.db.transcription import (
    get_one_unfinished_transcription,
    populate_transcription,
    set_transcription_failed,
    count_unfinished_transcriptions,
)
from transcribe.db import init_db
import schedule
import time
import multiprocessing
from yaspin import yaspin

import sentry_sdk
from transcribe.processor import sentry_report
if not DEVELOPMENT_MODE:
    sentry_sdk.init(
        dsn="https://6e57fad284954d52957fa64eb14c80cb@o536026.ingest.sentry.io/4504604755427328",
        traces_sample_rate=1.0
    )


API_BASE_URL = "https://transcribe.param.codes/api/v1"


def get_downloaded_file_path(token: str) -> str:
    return f"/tmp/{token}.opus"


def get_file_size(file_path: str) -> int:
    return Path(file_path).stat().st_size


def get_api_endpoint(token: str) -> str:
    return f"{API_BASE_URL}/internal/transcription/{token}/file"


def transcribe(token: str, version) -> str:
    connection = init_db()
    print("transcribing for token " + token)
    with yaspin(text="Transcribing...", timer=True):
        try:
            if DEVELOPMENT_MODE:
                output = {"transcription": "test output please ignore"}
                # output = version.predict(
                #     audio=get_downloaded_file_path(token))
            else:
                output = version.predict(
                    audio=get_api_endpoint(token), model='large')
        except Exception as e:
            print("Transcription failed with error: ", e)
            sentry_report(e)
            set_transcription_failed(connection, token, True)
            return
    print(f"got result for token : {token}!")
    result = json.dumps(output)
    populate_transcription(connection, token, result)


MAX_TIME_FOR_TRANSCRIPTION = 30 * 60  # 30 minutes


class Timeout(Exception):
    pass


class WhisperProcessor:
    def __init__(self):
        self.db = init_db()
        client = replicate.Client(api_token=REPLICATE_API_KEY)
        self.model = client.models.get("openai/whisper")
        self.version = self.model.versions.get(
            "30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed"
        )

    def process(self) -> None:
        count = count_unfinished_transcriptions(self.db)
        print("Unfinished transcriptions: " + str(count))
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
            set_transcription_failed(self.db, token, True)
            return

        print("downloaded link for token: " + token)
        result = None
        for _ in range(2):
            try:
                self.call_transcribe_with_timeout(
                    token,
                    MAX_TIME_FOR_TRANSCRIPTION,
                )
                break
            except TimeoutError as e:
                print("Transcription timed out: retrying...")
                time.sleep(2)
                continue
            except Exception as e:
                print("Transcription failed with error: ", e)
                sentry_report(e)
                set_transcription_failed(self.db, token, True)
                return
        else:
            print("Transcription kept timing out: failing")
            set_transcription_failed(self.db, token, True)
            return

        try:
            self.delete_downloaded_file(token)
            print(
                f"Done! Link: https://transcribe.param.codes/result/{token}"
            )
        except Exception as e:
            print("Transcription failed with error: ", e)
            sentry_report(e)
            set_transcription_failed(self.db, token, True)
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
            "postprocessors": [],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_link])

    def call_transcribe_with_timeout(self, token, timeout_sec):
        transcribe_process = multiprocessing.Process(
            target=transcribe,
            args=(
                token,
                self.version,
            ),
        )
        transcribe_process.start()
        transcribe_process.join(timeout_sec)
        if transcribe_process.is_alive():
            transcribe_process.terminate()
            raise TimeoutError


if __name__ == "__main__":
    processor = WhisperProcessor()
    schedule.every(10).seconds.do(processor.process)
    while True:
        schedule.run_pending()
        time.sleep(1)
