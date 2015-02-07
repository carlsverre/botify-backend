from botify import db

TABLES = {
    "stream": """
        CREATE TABLE IF NOT EXISTS stream (
            stream_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            created BIGINT NOT NULL,
            bots JSON NOT NULL,
            keep_alive BIGINT NOT NULL
        )
    """,

    "message": """
        CREATE TABLE IF NOT EXISTS message (
            message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            stream_id BIGINT NOT NULL,
            bot_id BIGINT,

            created BIGINT NOT NULL,
            updated BIGINT NOT NULL,
            pending BOOL DEFAULT 0,

            text VARCHAR(1024) NOT NULL,
            metadata JSON,

            INDEX(updated, message_id),
            INDEX(pending, updated)
    )
    """,

    "bot": """
        CREATE TABLE IF NOT EXISTS bot (
            bot_id BIGINT AUTO_INCREMENT PRIMARY KEY,

            created BIGINT NOT NULL,
            updated BIGINT NOT NULL,

            name VARCHAR(255) NOT NULL,
            sex VARCHAR(255) NOT NULL,
            seed_text_path TEXT NOT NULL,
            photo_url VARCHAR(1024) NOT NULL,

            INDEX(name)
        )
    """
}

def setup():
    with db.connect(db_name="information_schema", pooled=False) as c:
        print("bootstrapping db schema")
        c.query("CREATE DATABASE IF NOT EXISTS %s" % db.DB_NAME)
        c.query("USE %s" % db.DB_NAME)
        for name, t in TABLES.items():
            print("creating table %s" % name)
            c.query(t)
