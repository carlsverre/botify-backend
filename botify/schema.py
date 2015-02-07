from botify import db

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS stream (
        stream_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        created BIGINT NOT NULL,
        bots JSON NOT NULL
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS message (
        message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        stream_id BIGINT NOT NULL,
        bot_id BIGINT NOT NULL,

        created BIGINT NOT NULL,
        updated BIGINT NOT NULL,
        pending BOOL DEFAULT 0,

        text VARCHAR(1024) NOT NULL,
        metadata JSON NOT NULL,

        INDEX(updated, message_id),
        INDEX(pending, updated)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS bot (
        bot_id BIGINT AUTO_INCREMENT PRIMARY KEY,

        created BIGINT NOT NULL,
        updated BIGINT NOT NULL,

        name VARCHAR(255) NOT NULL,
        seed_text TEXT NOT NULL,
        sex VARCHAR(255) NOT NULL,
        photo_url VARCHAR(1024) NOT NULL,

        INDEX(name)
    )
    """
]

def setup():
    with db.connect(database="information_schema", pooled=False) as c:
        c.query("CREATE DATABASE IF NOT EXISTS %s" % db.DB_NAME)
        c.query("USE %s" % db.DB_NAME)
        for t in TABLES:
            c.query(t)
