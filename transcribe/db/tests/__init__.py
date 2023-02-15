from pathlib import Path
from unittest import TestCase
from transcribe.db import init_db, create_tables


class DatabaseTestCase(TestCase):
    def setUp(self) -> None:
        self.db = init_db("test.db")
        create_tables(self.db)

    def tearDown(self) -> None:
        self.db.close()
        Path.unlink(Path("test.db"))
