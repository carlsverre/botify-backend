import requests
from botify.util import json

def call(name, args):
    out = requests.post("http://localhost:5000/%s" % name, json.dumps(args))
    return out.json()

def generate(bot_id, metadata):
    return call("generate/%s" % bot_id, { "metadata": metadata })

def ingest(bot_id, text):
    return call("ingest/%s" % bot_id, { "text": text })

def symbols(text):
    return call("symbols", { "text": text })
