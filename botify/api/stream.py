import good as G

from botify import db
from botify.api.endpoints import endpoint
from botify.util import json
from botify.util.time_helpers import unix_timestamp

def create_stream():
    with db.connect() as c:
        return c.execute("""
            INSERT INTO stream (created, bots, keep_alive)
            VALUES (%s, %s, %s)
        """, unix_timestamp(), json.dumps([]), unix_timestamp())

def ping_stream(stream_id):
    with db.connect() as c:
        return c.query("""
            UPDATE stream SET keep_alive=%s
            WHERE stream_id = %s
        """, unix_timestamp(), stream_id)

def add_bot(stream_id, bot_id):
    with db.connect() as c:
        return c.query("""
            UPDATE stream SET bots=JSON_ARRAY_PUSH_STRING(bots, %s)
            WHERE stream_id=%s
        """, bot_id, stream_id)

def remove_bot(stream_id, bot_id):
    with db.connect() as c:
        bots = json.loads(c.get("SELECT bots FROM stream WHERE stream_id=%s", stream_id))
        bots.remove(bot_id)
        return c.query("""
            UPDATE stream SET bots=%s WHERE stream_id=%s
        """, json.dumps(bots), stream_id)

def create_message(stream_id, text, bot_id=None, pending=False, metadata=None):
    if metadata is None:
        metadata = {}
    now = unix_timestamp()

    with db.connect() as c:
        return c.execute("""
            INSERT INTO message (stream_id, bot_id, created, updated, pending, text, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, stream_id, bot_id, now, now, pending, text, json.dumps(metadata))

def query_messages(stream_id, updated_since=None, page=0, page_size=100):
    sql, params = [], []

    params.append(stream_id)

    if updated_since is not None:
        sql.append("updated >= %s")
        params.append(updated_since)

    params.append(page_size)
    params.append(page_size * page)

    if sql:
        where = "AND " + " AND ".join(sql)
    else:
        where = ""

    with db.connect() as c:
        return c.query("""
            SELECT
                message_id, bot_id, updated, pending, text
            FROM message
            WHERE stream_id = %%s
            %s
            ORDER BY bot_id ASC
            LIMIT %%s OFFSET %%s
        """ % where, *params)

@endpoint("stream/append", G.Schema({
    "stream_id": G.Maybe(int),
    "text": str
}))
def stream_append(params):
    if params.stream_id is None:
        params.stream_id = create_stream()
    message_id = create_message(
        stream_id=params.stream_id,
        text=params.text
    )

    return {
        "message_id": message_id,
        "stream_id": params.stream_id
    }

@endpoint("stream/query", G.Schema({
    "stream_id": int,
    "updated_since": G.Maybe(int),
    "page": G.Any(int, G.Default(0), G.Range(0, 999)),
    "page_size": G.Any(int, G.Default(100), G.Range(1, 200))
}))
def stream_query(params):
    return query_messages(**params)

@endpoint("stream/ping", G.Schema({ "stream_id": G.Maybe(int) }))
def stream_ping(params):
    return { "success": ping_stream(params.stream_id) }

@endpoint("stream/add_bot", G.Schema({
    "stream_id": int,
    "bot_id": int
}))
def stream_add_bot(params):
    return { "success": add_bot(params.stream_id, params.bot_id) }

@endpoint("stream/remove_bot", G.Schema({
    "stream_id": int,
    "bot_id": int
}))
def stream_remove_bot(params):
    return { "success": remove_bot(params.stream_id, params.bot_id) }
