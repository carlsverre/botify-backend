import sys
import logging

from tornado import web
from tornado import httpserver
from tornado import ioloop

from botify.util.super_thread import SuperThread
from botify.api_http_handler import ApiHttpHandler

logger = logging.getLogger(__name__)

class WebServer(SuperThread):
    sleep = 0

    def setup(self):
        self.host = self.context["host"]
        self.port = self.context["port"]
        self._loop = ioloop.IOLoop.instance()

    def work(self):
        app = web.Application(
            handlers=[
                (r"/api/(?P<name>.*)/?", ApiHttpHandler),
            ],
            compress_response=True,
            log_function=self._tornado_logger
        )

        server = httpserver.HTTPServer(request_callback=app, io_loop=self._loop)
        server.listen(address=self.host, port=self.port)

        self._set_interval(self._check_closed, 1000)
        self._loop.start()

    def _set_interval(self, callback, interval):
        cb = ioloop.PeriodicCallback(callback, interval, io_loop=self._loop)
        cb.start()

    def _tornado_logger(self, handler):
        exc_info = False
        if handler.get_status() < 400:
            log_method = logger.info
        elif handler.get_status() < 500:
            log_method = logger.warning
        else:
            exc_info = sys.exc_info() or False
            log_method = logger.error

        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %.2fms", handler.get_status(), handler._request_summary(), request_time, exc_info=exc_info)

    def _check_closed(self):
        if self.stopping():
            self._loop.stop()
