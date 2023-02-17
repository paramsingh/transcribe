import json
import requests

BASE_URL = 'https://transcribe.param.codes/api/v1'


def submit_for_transcription(video_id):
    url = f'{BASE_URL}/transcribe'
    video_link = f'https://www.youtube.com/watch?v={video_id}'
    r = requests.post(
        url,
        json={
            'link': video_link
        },
        headers={
            "Content-Type": "application/json",
        },
    )
    r.raise_for_status()
    return r.json()['id']


with open('ycombinator_videos.json') as f:
    videos = json.load(f)

NUMBER_OF_VIDEOS_TO_SUBMIT = 50
OFFSET = 0

for video in videos[OFFSET:OFFSET + NUMBER_OF_VIDEOS_TO_SUBMIT]:
    print(video['title'])
    token = submit_for_transcription(video['id'])
    print(f"Submitted! token: {token}")
