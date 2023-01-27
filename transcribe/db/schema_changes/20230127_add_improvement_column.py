from transcribe.db import init_db


def main():
    """Add a column to the transcription table to store improvement data."""
    print("Adding column!")
    connection = init_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        ALTER TABLE transcription ADD COLUMN improvement TEXT;
    """
    )
    connection.commit()
    connection.close()
    print("Done!")


if __name__ == "__main__":
    main()
