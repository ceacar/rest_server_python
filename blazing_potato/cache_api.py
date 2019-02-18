from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
import cache
from errors import *
import json


class CacheAPI(MethodView):
    """
    use cacher to save cache
    POST /save
    GET /get/<key>
    """
    def format_result(self, err, value):
        res = {"errors":err, "result" : value}
        return json.dumps(res)

    def post(self):
        """
        there should be two field called "key" and "value" in json
        """
        req_data = request.get_json()
        try:
            key = req_data.get("key", "")
            value = req_data.get("value", "")
            print("value is",value,type(value))
            if not key:
                return (self.format_result("key empty", ""),400)
            if not value:
                return (self.format_result("value empty", ""),400)

            cacher = cache.get_cacher()
            cacher.save(key, value)

            return (self.format_result("", "saved"), 200)
        except Exception:
            abort("Unknown Error", 501)

    def get(self, key: str):
        try:
            res = cache.get_cacher().get(key)
            if res:
                return (self.format_result("", res), 200)
            else:
                return (self.format_result("invalid key", res), 400)

        except Exception:
            abort("Unknown Error", 501)
