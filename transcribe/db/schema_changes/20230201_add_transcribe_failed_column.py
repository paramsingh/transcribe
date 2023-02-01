from transcribe.db import init_db


def main():
    """Add a column to the transcription table."""
    print("Adding column transcribe_failed!")
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        ALTER TABLE transcription ADD COLUMN transcribe_failed BOOLEAN DEFAULT 0;
    """
    )
    connection.commit()
    connection.close()
    print("Done!")


if __name__ == "__main__":
    main()
