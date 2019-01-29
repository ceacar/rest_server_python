from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
from weathertracker import utils
from weathertracker import cache
from weathertracker.utils.misc import (
    parse_json_param,
    format_response
)
from weathertracker.utils.conversion import(
    to_datetime
)
from weathertracker.utils.errors import *


class MeasurementsAPI(MethodView):

    # features/01-measurements/01-add-measurement.feature
    def post(self):
        """
            exmaple input:
              | timestamp                  | temperature | dewPoint | precipitation |
              | "2015-09-01T16:00:00.000Z" | 27.1        | 16.7     | 0             |

        """
        req_data = request.get_json()

        try:
            timestamp, temperature, dewPoint, precipitation = parse_json_param(req_data)

        except (DatetimeConversionException, InvalidTimestampFormatException) as err:
            return (err.message, 400)

        except FloatNumberConversionException as err:
            return (err.message, 400)

        try:
            cache.get_cacher().save(timestamp, temperature, dewPoint, precipitation)
            #location header need to be like /measurements/2015-09-01T16:00:00.000Z
            timestamp = req_data.get("timestamp", "")
            return ("\n", 201, {'location': '/measurements/{ts}'.format(ts = timestamp)})
        except Exception:
            abort("Unknown Error", 501)

    # features/01-measurements/02-get-measurement.feature
    def get(self, timestamp: '2015-09-01T16:00:00.000Z'):
        try:
            timestamp = to_datetime(timestamp)
            res_tuple = cache.get_cacher().get(timestamp)
            if res_tuple:
                timestamp, temperature, dewPoint, precipitation = res_tuple
                return (format_response(timestamp, temperature, dewPoint, precipitation), 200)
            else:
                return ("Not Found\n", 404)

        except DatetimeConversionException as err:
            return (err, 400)
        except Exception:
            abort(501)
