import logging

from botify.util.super_thread import SuperThread
from botify.util import json
from botify import db

from botify.api import stream
from botify.api import bot
import botify.joyo_client as client

STREAM_ID = 1

class Podcast(SuperThread):
    sleep = 1

    def setup(self):
        self.logger = logging.getLogger(__name__)
        # ensure stream exists
        stream.create_stream(stream_id=STREAM_ID)

    def work(self):
        pass

    def add_bot_to_stream(self):
        all_bots = bot.query_bots()
