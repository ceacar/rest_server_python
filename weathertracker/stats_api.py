from flask import request, jsonify
from flask.views import MethodView
from werkzeug.exceptions import abort
from weathertracker.stats import get_stats
from weathertracker import cache
from weathertracker.utils.conversion import(
    to_datetime
)
from weathertracker.utils.errors import *
from weathertracker.utils.misc import (
    parse_stat_param,
)



class StatsAPI(MethodView):
    # features/02-stats/01-get-stats.feature
    def get(self):
        stats = request.args.getlist("stat")
        metrics = request.args.getlist("metric")
        from_datetime = request.args.get("fromDateTime")
        to_datetime = request.args.get("toDateTime")

        try:
            stats, metrics, from_datetime, to_datetime = parse_stat_param(stats, metrics, from_datetime, to_datetime)
        except (InvalidMetricException, NoStatsException, FloatNumberConversionException, DatetimeConversionException) as err:
            return (err, 400)

        stats = get_stats(stats, metrics, from_datetime, to_datetime)
        return stats
