from botify.util.super_thread import SuperThread
from tornado.concurrent import Future
import Queue
import logging

logger = logging.getLogger(__name__)
REQUEST_QUEUE = Queue.Queue()
NUM_WORKERS = 20

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
            response = self.params
            self.future.set_result(response)
        except Exception as e:
            self.future.set_exception(e)

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
