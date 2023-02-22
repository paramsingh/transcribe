import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the YouTube Data API v3 client
DEVELOPER_KEY = 'AIzaSyBdkFujlFFLTBHUM0_zGLgJjm0A4TbwaUI'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
MAX_RESULTS = 50  # Max number of results per page


def get_ycombinator_videos(next_page_token=None):
    # Get YCombinator's channel ID
    channel_id = 'UCcefcZRL2oaA_uBNeo5UOWg'
    print(channel_id)

    # Build the client object
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Set up the search request
    search_response = youtube.search().list(
        channelId=channel_id,
        type='video',
        part='id,snippet',
        maxResults=MAX_RESULTS,
        pageToken=next_page_token,
    ).execute()

    # Parse the search results to extract video IDs and titles
    videos = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        title = search_result['snippet']['title']
        videos.append({'id': video_id, 'title': title})

    # Check if there are more results and fetch them recursively
    next_page_token = search_response.get('nextPageToken')
    if next_page_token:
        videos.extend(get_ycombinator_videos(next_page_token))

    return videos


# Call the function to get the list of YCombinator's videos
videos = get_ycombinator_videos()
with open('ycombinator_videos.json', 'w') as f:
    print(json.dumps(videos, indent=2), file=f)

# print(f"{video['title']}: https://www.youtube.com/watch?v={video['id']}")
