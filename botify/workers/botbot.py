import logging
from collections import defaultdict

from botify.util.super_thread import SuperThread
from botify.util import json

from botify.api import stream
import botify.joyo_client as client

NUM_MESSAGE_CONTEXT = 5

class BotBot(SuperThread):
    sleep = 1

    def setup(self):
        self.dequeue_lock = self.context["dequeue_lock"]
        self.index = self.context["index"]
        self.logger = logging.getLogger("botbot-%s" % self.index)

    def work(self):
        # 1. find a candidate pending message in any stream
        with self.dequeue_lock:
            candidate = stream.get_pending_message()

        if not candidate:
            return

        stream_id = candidate.stream_id
        bot_id = candidate.bot_id

        self.logger.info("Grabbed %s" % candidate)

        # 2. get last N messages from the stream
        messages = stream.query_messages(
            stream_id=stream_id,
            pending=False,
            order_by="updated",
            order_dir="DESC",
            page_size=NUM_MESSAGE_CONTEXT,
            null_metadata=False
        )

        # 3. merge message metadata
        metadata = defaultdict(lambda: 0)
        for message in messages:
            for k, v in message.metadata.items():
                metadata[k] += v

        # 4. send generate to joyo
        try:
            new_message = client.generate(bot_id, metadata)
            if not new_message["success"]:
                raise Exception(json.pretty_dumps(new_message))
            else:
                new_text = new_message["body"]
                new_metadata = new_message.get("symbols", {})
        except Exception as e:
            self.logger.error("Client call failure: %s" % str(e))
            return

        # 5. post a new pending message
        stream.add_pending_message(stream_id, bot_id)

        # 6. post the new message
        stream.update_message(
            message_id=candidate.message_id,
            text=new_text,
            metadata=new_metadata
        )
