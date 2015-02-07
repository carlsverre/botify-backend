import math
import time
from datetime import datetime

def unix_timestamp():
    return math.floor(time.time())

def to_unix_timestamp(timestamp):
    """ A helper to convert either a datetime or timestamp to timestamp. """
    if isinstance(timestamp, datetime):
        return math.floor(timestamp.timestamp())
    else:
        return timestamp
