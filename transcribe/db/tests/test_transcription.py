from transcribe.db.tests import DatabaseTestCase
from transcribe.db.transcription import (
    create_transcription,
    add_improvement,
    add_summary,
    get_one_unimproved_transcription,
)


class TranscriptionTestCase(DatabaseTestCase):

    def test_create_transcription(self):
        token = create_transcription(
            self.db, "https://example.com", None, "result")
        self.assertIsNotNone(token)

    def test_get_one_unimproved_transcription_returns_transcriptions_without_embeddings(self):
        token = create_transcription(
            self.db, "https://example.com", None, "result")
        self.assertIsNotNone(token)
        # add improvement and summary
        add_improvement(self.db, 'improved text', token)
        add_summary(self.db, 'summary text', token)

        # get unimproved transcription
        transcription = get_one_unimproved_transcription(self.db)
        self.assertIsNotNone(transcription)
        self.assertEqual(transcription['token'], token)
