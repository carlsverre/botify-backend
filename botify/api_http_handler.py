from tornado import web
from tornado import gen

from botify.exceptions import ApiException, JSONDecodeError
from botify.api import pool
from botify.util import json

class ApiHttpHandler(web.RequestHandler):
    def prepare(self):
        """ Make sure that all responses include our access-control-allow-origin policy. """
        self.set_header('Content-Type', 'application/json')
        self.set_header('Cache-control', 'no-cache')
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self):
        """ ``options`` is implemented to handle Access-Control-Allow-Origin requests. """
        self.set_status(204)
        self.finish()

    @web.removeslash
    @gen.coroutine
    def post(self, name):
        try:
            params = self._params()
            response = yield pool.query(name, params)
            self._respond_success(response)
        except Exception as err:
            self._respond_error(err)

    def _params(self):
        """ Decode a params dictionary from the request body. """
        body = self.request.body.strip()
        if not body:
            return {}

        try:
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise JSONDecodeError(str(e))

    def _respond_success(self, data):
        self._finish(200, data)

    def _respond_error(self, error):
        status_code = 400 if isinstance(error, ApiException) else 500
        data = {
            "error": str(error),
            "error_type": error.__class__.__name__
        }

        self._finish(status_code, data)

    def _finish(self, status_code, data):
        self.set_status(status_code)
        self._write_json(data)
        self.finish()

    def _write_json(self, data):
        data = json.dumps(data)
        self.write(data + "\n")
