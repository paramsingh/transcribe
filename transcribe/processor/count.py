import json
from transcribe.db.db_utils import get_flask_db
import transcribe.db.embedding as embedding_db

class EmbeddingsMerger:
    def init(self):
        with open('../../ycombinator_videos.json', 'r') as f:
            self.videos = [f"https://www.youtube.com/watch?v={x['id']}" for x in json.load(f)]

    def get_embeddings(self):
        db = get_flask_db()
        embeddings = [embedding_db.get_embeddings_for_link(video) for video in self.videos]
        print(embeddings)

if __name__ == '__main__':
    embedding_merger = EmbeddingsMerger()
    embedding_merger.get_embeddings()

