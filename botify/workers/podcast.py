import logging
import time
import random

from botify.util.super_thread import SuperThread

from botify.api import stream
from botify.api import bot

STREAM_ID = 1

MIN_CHANGE = 5
MAX_CHANGE = 5

MIN_BOTS = 2
MAX_BOTS = 4

class Podcast(SuperThread):
    sleep = 2

    def setup(self):
        self.logger = logging.getLogger(__name__)
        # ensure stream exists
        stream.create_stream(stream_id=STREAM_ID)
        self.next_change = time.time() + (MAX_CHANGE / 2)

    def work(self):
        # make sure the stream stays alive
        stream.ping_stream(STREAM_ID)

        if time.time() > self.next_change:
            self.next_change = time.time() + random.randint(MIN_CHANGE, MAX_CHANGE)

            current_bots = stream.bots_in_stream(stream_id=STREAM_ID)
            all_bots = bot.query_bots()

            self.logger.info("Podcast currently has %d participants" % len(current_bots))

            if len(current_bots) > MIN_BOTS:
                to_remove = random.choice(current_bots)
                current_bots.remove(to_remove)

                to_remove_bot = None
                for b in all_bots[:]:
                    if b.bot_id == to_remove:
                        all_bots.remove(b)
                        to_remove_bot = b

                self.logger.info("Removing %s from stream" % to_remove_bot.name)
                stream.remove_bot(STREAM_ID, to_remove)
                stream.create_message(STREAM_ID,
                    "%s has left the room" % to_remove_bot.name,
                    metadata={ to_remove_bot.name: 1 })

            if len(current_bots) < MAX_BOTS and random.random() > 0.5:
                to_add = random.choice(all_bots)

                self.logger.info("Adding %s to stream" % to_add.name)
                stream.create_message(STREAM_ID,
                    "%s has joined the room" % to_add.name,
                    metadata={ to_add.name: 1 })
                stream.add_bot(STREAM_ID, to_add.bot_id)
