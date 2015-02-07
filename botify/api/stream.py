import good as G
import random

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

def create_message(stream_id, text, bot_id=None, pending=False, pending_time=None, metadata=None):
    if metadata is None:
        metadata = {}
    now = unix_timestamp()

    with db.connect() as c:
        return c.execute("""
            INSERT INTO message (stream_id, bot_id, created, updated, pending, pending_time, text, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, stream_id, bot_id, now, now, pending, pending_time, text, json.dumps(metadata))

def get_pending_message():
    candidates = query_messages(
        pending=True,
        working=False,
        pending_until=unix_timestamp(),
        order_by="pending_time",
        order_dir="ASC",
        page_size=1
    )
    if candidates:
        candidate = candidates[0]
        with db.connect() as c:
            c.execute(
                "UPDATE message SET working=True WHERE message_id=%s",
                candidate.message_id)
        return candidate

def add_pending_message(stream_id, bot_id):
    target_time = unix_timestamp() + random.uniform(2, 10)
    create_message(
        stream_id=stream_id,
        text="",
        bot_id=bot_id,
        pending=True,
        pending_time=target_time
    )

def update_pending_message(message_id, text, metadata):
    with db.connect() as c:
        return c.execute("""
            UPDATE message
            SET text=%s, metadata=%s, updated=%s, pending=False
            WHERE message_id=%s
        """, text, json.dumps(metadata), unix_timestamp(), message_id)

def query_messages(stream_id=None, updated_since=None, pending_until=None, page=0, page_size=100, pending=None, working=None, order_by="updated", order_dir="DESC", null_metadata=None):
    sql, params = [], []

    if stream_id is not None:
        sql.append("stream.stream_id = %s")
        params.append(stream_id)
    if updated_since is not None:
        sql.append("updated >= %s")
        params.append(updated_since)
    if pending_until is not None:
        sql.append("pending_time < %s")
        params.append(pending_until)
    if working is not None:
        sql.append("working = %s")
        params.append(working)
    if pending is not None:
        sql.append("pending = %s")
        params.append(pending)
    if null_metadata is not None:
        if null_metadata:
            sql.append("metadata IS NULL")
        else:
            sql.append("metadata IS NOT NULL")

    params.append(page_size)
    params.append(page_size * page)

    if sql:
        where = "AND " + " AND ".join(sql)
    else:
        where = ""

    keep_alive = unix_timestamp() - 60
    with db.connect() as c:
        rows = c.query("""
            SELECT
                stream.stream_id, message_id, bot_id, updated, pending, text, metadata
            FROM message
            INNER JOIN stream ON message.stream_id = stream.stream_id
            WHERE stream.keep_alive > %s
            %s
            ORDER BY %s %s
            LIMIT %%s OFFSET %%s
        """ % (keep_alive, where, order_by, order_dir), *params)

        for row in rows:
            row.metadata = json.loads(row.metadata) if row.metadata else None
        return rows

def add_bot(stream_id, bot_id):
    with db.connect() as c:
        out = c.query("""
            UPDATE stream SET bots=JSON_ARRAY_PUSH_STRING(bots, %s)
            WHERE stream_id=%s
        """, bot_id, stream_id)

    add_pending_message(stream_id, bot_id)
    return out

def remove_bot(stream_id, bot_id):
    with db.connect() as c:
        bots = json.loads(c.get("SELECT bots FROM stream WHERE stream_id=%s", stream_id))
        bots.remove(bot_id)
        return c.query("""
            UPDATE stream SET bots=%s WHERE stream_id=%s
        """, json.dumps(bots), stream_id)

@endpoint("stream/create")
def stream_create(params):
    return { "stream_id": create_stream() }

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
    "page_size": G.Any(int, G.Default(100), G.Range(1, 200)),
    "order_dir": G.Any("DESC", "ASC", G.Default("DESC")),
    "order_by": G.Any("created", "updated", G.Default("updated"))
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
