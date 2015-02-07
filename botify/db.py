from memsql.common import database, connection_pool

PoolConnectionException = connection_pool.PoolConnectionException
MySQLError = database.MySQLError

import os
DB_HOST = os.environ("DB_HOST")
DB_PORT = os.environ("DB_PORT")
DB_NAME = "botify"

POOL = connection_pool.ConnectionPool()

def connect(host=DB_HOST, port=DB_PORT, user="root", password="", db_name=DB_NAME, pooled=True):
    target = None
    if pooled:
        target = POOL
    else:
        target = database

    if target:
        return target.connect(host=host, port=int(port), user=user, password=password, database=db_name)
