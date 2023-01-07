# Example run of this in Google Colab here:
# https://colab.research.google.com/drive/1BFauKBulKKSllkGVDhXnJQOIUD-qkgXL#scrollTo=O8f2WlCW8qLR
import whisper
import json
import yt_dlp


def download_video(yt_link: str, path: str):
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


def transcribe(filename: str) -> dict:
    model = whisper.load_model("base")
    print("transcribing...")
    return model.transcribe(filename)


if __name__ == "__main__":
    youtube_link = "https://www.youtube.com/watch?v=WHoWGNQRXb0"
    download_video(youtube_link, "audio.opus")
    print("downloaded!")
    result = transcribe("audio.opus")
    with open("result.json", "w") as f:
        print(json.dumps(result, indent=4), file=f)
    print("Done!")
