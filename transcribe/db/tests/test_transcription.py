from transcribe.db.tests import DatabaseTestCase
from transcribe.db.transcription import create_transcription


class TranscriptionTestCase(DatabaseTestCase):

    def test_create_transcription(self):
        token = create_transcription(
            self.db, "https://example.com", None, "result")
        self.assertIsNotNone(token)
