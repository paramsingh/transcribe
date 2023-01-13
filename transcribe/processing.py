import replicate
import yt_dlp
import os
import json
import base64


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


if __name__ == "__main__":

    youtube_link = "https://www.youtube.com/watch?v=WHoWGNQRXb0"
    download_video(youtube_link, "audio.opus")
    print("downloaded!")

    os.putenv("REPLICATE_API_TOKEN", "c2b638b386c23db5caf2faedf8ea6e30f968de10")
    model = replicate.models.get("openai/whisper")
    # write a small note about versions of the model
    version = model.versions.get("30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed")
    with open('audio.opus', 'rb') as f:
        base64_audio_string = base64.b64encode(f.read())
    # output = version.predict(audio=f"data:audio/opus,{base64_audio_string}")
    # output = version.predict(audio=f"data:audio/opus;base64, {base64_audio_string}")
    output = version.predict(audio="audio.opus")

    with open("result.json", "w") as f:
        print(json.dumps(output, indent=4), file=f)
    print("Done!")
