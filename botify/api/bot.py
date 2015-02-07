import good as G

from botify import db
from botify.api.endpoints import endpoint
from botify.util.time_helpers import unix_timestamp

def create_bot(name, sex, seed_text_path, photo_url):
    now = unix_timestamp()
    with db.connect() as c:
        return c.execute("""
            INSERT INTO bot (created, updated, name, sex, seed_text_path, photo_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, now, now, name, sex, seed_text_path, photo_url)

def query_bots(name=None, page=0, page_size=100):
    sql, params = [], []

    if name is not None:
        sql.append("name LIKE %s")
        params.append(name)

    params.append(page_size)
    params.append(page_size * page)

    if sql:
        where = "WHERE " + " AND ".join(sql)
    else:
        where = ""

    with db.connect() as c:
        return c.query("""
            SELECT * FROM bot
            %s
            ORDER BY bot_id ASC
            LIMIT %%s OFFSET %%s
        """ % where, *params)

def get_bot(bot_id):
    with db.connect() as c:
        return c.get("""
            SELECT * FROM bot
            WHERE bot_id = %s
        """, bot_id)

@endpoint("bot/query", G.Schema({
    "name": G.Maybe(str),
    "page": G.Any(int, G.Default(0), G.Range(0, 999)),
    "page_size": G.Any(int, G.Default(100), G.Range(1, 200))
}))
def bot_query(params):
    return query_bots(**params)

@endpoint("bot/get", G.Schema({ "bot_id": int }))
def bot_get(params):
    return get_bot(params.bot_id)
