from functools import wraps
from botify.util.attr_dict import AttrDict
from botify import exceptions

ENDPOINTS = {}

def endpoint(name, schema=None):
    def _deco(wrapped):
        @wraps(wrapped)
        def _wrap(params):
            if schema is not None:
                params = AttrDict(schema(params))

            return wrapped(params)

        ENDPOINTS[name] = _wrap
        return _wrap

    return _deco

def call(name, props):
    endpoint = ENDPOINTS.get(name)
    if endpoint is None:
        raise exceptions.ApiException("Endpoint not found: %s" % name)
    return endpoint(props)

# import all endpoints here

from botify.api import stream  # noqa
from botify.api import bot  # noqa
