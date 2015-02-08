import logging

from botify.util.super_thread import SuperThread
from botify.util import json

from botify.api import stream
import botify.joyo_client as client

class UserInputParser(SuperThread):
    sleep = 1

    def setup(self):
        self.logger = logging.getLogger(__name__)

    def work(self):
        # get null metadata messages and process them
        pending = stream.query_messages(null_metadata=True)

        self.logger.info("processing %d messages" % len(pending))

        for msg in pending:
            try:
                new_message = client.symbols(msg.text)
                if not new_message["success"]:
                    raise Exception(json.pretty_dumps(new_message))
                else:
                    new_metadata = new_message.get("symbols", {})
            except Exception as e:
                self.logger.error("Client call failure: %s" % str(e))
                return

            stream.update_message(
                message_id=pending.message_id,
                text=pending.text,
                metadata=new_metadata)
