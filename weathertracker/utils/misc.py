import json

from weathertracker.utils.errors import(
    DatetimeConversionException,
    FloatNumberConversionException
)

from weathertracker.utils.conversion import(
    to_datetime,
    to_float,
    to_timestamp_utc_str
)

from weathertracker.utils.errors import *

def parse_json_param(json_input: 'json format:{}') \
        -> 'timestamp(datetime), temperature(float), dewPoint(float), precipitation(float)':

    timestamp = to_datetime(json_input.get("timestamp", ""))
    temperature = to_float(json_input.get('temperature', 0))
    dewPoint = to_float(json_input.get('dewPoint',0))
    precipitation = to_float(json_input.get('precipitation', 0))

    return timestamp, temperature, dewPoint, precipitation

def format_response(timestamp: 'Datetime', temperature: 'float',
                    dewPoint: 'float', precipitation: 'float') -> 'json format output {}':
    res = {}
    res["timestamp"] = to_timestamp_utc_str(timestamp)
    res["temperature"] = temperature
    res["dewPoint"] = dewPoint
    res["precipitation"] = precipitation
    return json.dumps(res)

def calculate_average(a_float_list: '[float]') -> 'float':
    res = sum(a_float_list)/len(a_float_list)
    return round(res, 1)

def filter_non_zero_float(a_float_list) -> '[flot]':
    return list(filter(lambda x: x >0.00000000000001, a_float_list))

def parse_stat_param(stats: '[str]', metrics: 'str', from_dt: 'str',
                     to_dt: 'str') -> 'str, str, datetime, datetime':
    fm_dt = to_datetime(from_dt)
    to_dt = to_datetime(to_dt)

    if not metrics:
        raise InvalidMetricException("metric empty")
    if not stats:
        raise NoStatsException("stats empty")

    return stats, metrics, fm_dt, to_dt

def format_stats_result(data_arr: 'metric dict like {"temperature": [float], ...}',
                        stats: '[str]', metrics: '[str]') -> 'json str':
    """
    example of returns:
        [
        {"value": 22.4, "metric": "temperature", "stat": "min"},
        {"value": 22.4, "metric": "temperature", "stat": "max"},
        {"value": 22.4, "metric": "temperature", "stat": "average"},
        {"value": 18.6, "metric": "dewPoint", "stat": "min"},
        {"value": 18.6, "metric": "dewPoint", "stat": "max"},
        {"value": 18.6, "metric": "dewPoint", "stat": "average"},
        {"value": 142.2, "metric": "precipitation", "stat": "min"},
        {"value": 142.2, "metric": "precipitation", "stat": "max"},
        {"value": 142.2, "metric": "precipitation", "stat": "average"}
    """
    res = []
    for metric in metrics:
        for i in range(len(stats)):
            num_list_by_metric = data_arr[metric]
            if num_list_by_metric:
                output_msg = {}
                output_msg["metric"] = metric
                output_msg["stat"] = stats[i]
                output_msg["value"] = num_list_by_metric[i]
                res.append(output_msg)
    sorted_res = sorted(res, key=lambda x:sorted(x.keys()))
    return json.dumps(sorted_res)
