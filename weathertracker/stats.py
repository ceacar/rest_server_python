from werkzeug.exceptions import abort
from weathertracker import cache
from weathertracker.utils.errors import *
from weathertracker.utils.misc import(
	format_stats_result,
    parse_stat_param,
    calculate_average,
    filter_non_zero_float,
)


__STAT_FUNC = { "min": min, "max": max, "average": calculate_average}


def calculate_stat(metric_res_dict: 'a dict of metrics {"temperature": [float], ...}',
                   stats: '[str] min, average, max etc...') -> '[float]':
    res = {}
    for metric in metric_res_dict:
        res[metric] = []
        for stat in stats:
            arr_for_compute = metric_res_dict[metric]
            filtered_0_arr = filter_non_zero_float(arr_for_compute)
            if filtered_0_arr:
                #min max doesn't work with empty arr
                func = __STAT_FUNC[stat]
                res[metric].append(func(filtered_0_arr))

    return res


def get_stats(stats: '[str]', metrics: 'str', from_datetime: 'str', to_datetime: 'str'):
    """
    expected input:
      | param        | value                    |
      | stat         | min                      |
      | stat         | max                      |
      | stat         | average                  |
      | metric       | temperature              |
      | fromDateTime | 2015-09-01T16:00:00.000Z |
      | toDateTime   | 2015-09-01T17:00:00.000Z |
    expected output:
      | metric        | stat      | value |
      | "temperature" | "min"     | 27.1  |
      | "temperature" | "max"     | 27.5  |
      | "temperature" | "average" | 27.3  |

    """
    try:
        cacher = cache.get_cacher()
        res_dict = cacher.select(from_datetime, to_datetime, metrics)
        res_stats = calculate_stat(res_dict, stats)
        res_json = format_stats_result(res_stats, stats, metrics)
        return (res_json, 200)
    except (InvalidMetricException, DatetimeConversionException, FloatNumberConversionException, NoStatsException) as err:
        return (err.message, 400)
