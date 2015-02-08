from botify.util.super_thread import SuperThread
from tornado.concurrent import Future
import Queue
import sys
import logging

from botify.api import endpoints

logger = logging.getLogger(__name__)
REQUEST_QUEUE = Queue.Queue()
NUM_WORKERS = 10

class ApiWorker(SuperThread):
    sleep = 0.1

    def work(self):
        try:
            request = REQUEST_QUEUE.get(timeout=0.1)
            request.execute()
        except Queue.Empty:
            pass

class ApiRequest(object):
    def __init__(self, name, params, future):
        self.name = name
        self.params = params
        self.future = future

    def execute(self):
        try:
            response = endpoints.call(self.name, self.params)
            self.future.set_result(response)
        except Exception:
            self.future.set_exc_info(sys.exc_info())

def setup(thread_manager):
    for i in range(NUM_WORKERS):
        thread_manager.add(ApiWorker)

def status():
    logger.info('%d queries outstanding' % (REQUEST_QUEUE.qsize()))

def query(name, params):
    future = Future()
    request = ApiRequest(name, params, future)
    REQUEST_QUEUE.put(request)
    return future
