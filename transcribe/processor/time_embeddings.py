import json
from transcribe.db.db_utils import get_flask_db
import transcribe.db.transcription as transcription_db
from transcribe.processor.improve import Improver
import time


class EmbeddingsMerger:
    def __init__(self):
        self.videos = []
        with open('../../ycombinator_videos.json', 'r') as f:
            self.videos = [f"https://www.youtube.com/watch?v={x['id']}" for x in json.load(f)]

    def _get_text_for_all_videos(self):
        db = get_flask_db()
        raw_texts = [transcription_db.get_transcription_by_link(get_flask_db(), video) for video in self.videos]
        return [text['result'] for text in raw_texts]

    def merged_embedding_time(self):
        improver = Improver()
        start = time.process_time()
        improver.create_embeddings_n(self._get_text_for_all_videos(), 'y_combinator_group')
        return time.process_time() - start


if __name__ == '__main__':
    embedding_merger = EmbeddingsMerger()
    print(embedding_merger.merged_embedding_time())

