# Example run of this in Google Colab here:
# https://colab.research.google.com/drive/1BFauKBulKKSllkGVDhXnJQOIUD-qkgXL#scrollTo=O8f2WlCW8qLR
import whisper
import json
import yt_dlp
import schedule
import time
from sqs import WhisperSQSConsumer, WhisperSQSPublisher


class WhisperProcessor:

    def __init__(self):
        self.producer = WhisperSQSPublisher()
        self.consumer = WhisperSQSConsumer()
        self.path = "audio.opus"

    def process(self):
        yt_link, receipt_handle = self.consumer.consume()

        if not yt_link:
            print("Empty receive, will try again in next cycle")
            return 

        self.download_video(yt_link, self.path)
        print("downloaded!")
        result = self.transcribe(self.path)
        self.producer.publish(yt_link, result)
        self.consumer.delete_message(receipt_handle)
        print("Done!")


    def download_video(self, yt_link: str, path: str):
        """Use yt_dlp to download audio from a youtube link to path"""
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


    def transcribe(self, filename: str) -> dict:
        model = whisper.load_model("base")
        print("transcribing...")
        return model.transcribe(filename)


    if __name__ == "__main__":
        processor = WhisperProcessor()
        schedule.every(5).minutes.do(processor.process())
        while True:
            schedule.run_pending()
            time.sleep(1)
