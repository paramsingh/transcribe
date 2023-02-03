from transcribe.db import init_db
import transcribe.login.db.schema_change.create_tables as login_create_tables


def main():
    """ Creating tables for login. """
    print("Creating tables for login...")
    connection = init_db()
    cursor = connection.cursor()
    login_create_tables.schema_change(cursor)
    print("Adding user_id column to transcription table...")
    cursor.execute(
        """
            ALTER TABLE transcription ADD COLUMN user_id INTEGER REFERENCES user(id);
        """
    )
    print("Done!")


if __name__ == "__main__":
    main()
