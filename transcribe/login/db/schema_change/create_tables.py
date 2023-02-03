from transcribe.login.db import create_session_table, create_user_table, create_magic_link_table


def schema_change(cursor):
    # Create user table
    print("Creating user table...")
    create_user_table(cursor)
    print("Done!")

    # Create session table
    print("Creating session table...")
    create_session_table(cursor)
    print("Done!")

    # Create magic link table
    print("Create magic link table...")
    create_magic_link_table(cursor)
    print("Done!")
