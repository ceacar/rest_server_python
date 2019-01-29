import weathertracker
from weathertracker.utils.errors import (
    InvalidMetricException,
)

from weathertracker.utils.misc import (
    calculate_average,
)


__EXPECTED_TIMESTAMP_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"

class Cacher:

    def __init__(self):
        self.temperature_metric = {}
        self.metric_position = {
            "timestamp": 0,
            "temperature": 1,
            "dewPoint": 2,
            "precipitation": 3,
        }


    def save(self, timestamp_pk: 'DateTime 2015-09-01T16:00:00.000Z', temperature: 'float 22.4',
             dewPoint: 'float 22.4', precipitation: 'float 142.2' ):
        """
            Metric Name Type    Example Notes
            timestamp   DateTime    "2015-09-01T16:00:00.000Z"  Always sent as an ISO-8061 string in UTC
            temperature float   22.4    in ° C
            dewPoint    float   18.6    in ° C
            precipitation   float   142.2   in mm
        """
        self.temperature_metric[timestamp_pk] = (timestamp_pk, temperature, dewPoint, precipitation)

    def delete(self, timestamp: 'DateTime'):
        target = self.temperature_metric.get(timestamp, None)
        if target:
            del self.temperature_metric[timestamp]

    def get(self, timestamp: 'DateTime') -> '(DateTime, float, float, float)':
        return self.temperature_metric.get(timestamp, None)

    def check_if_metric_name_valid(self, metrics):

        keys = list(self.metric_position.keys())
        is_metric_valid = True

        for metric in metrics:
            if metric not in keys:
                return False

        return is_metric_valid

    def filter_by_dts(self, from_dt: 'Datetime', to_dt: 'Datetime'):
        res = []
        for k in self.temperature_metric:
            if to_dt > k >= from_dt:
                res.append(self.temperature_metric[k])

        return res

    def filter_by_metric(self, temperature_metric: 'list of self.temperature_metric',
                         metrics: '[str] temperature, etc..'
                        ) -> 'dict of metrics like {"temperature":[], ...}':

        if not self.check_if_metric_name_valid(metrics):
            raise InvalidMetricException("{0} metric is not supported".format(metrics))

        res = {}
        for metric in metrics:
            field_to_keep = self.metric_position[metric]
            res[metric] = []
            for composite_tuple in temperature_metric:
                res[metric].append(composite_tuple[field_to_keep])
            res[metric] = sorted(res[metric])

        return res

    def select(self, from_dt: 'Datetime', to_dt: 'Datetime', 
               metric: 'str:field to keep') -> 'metric dict {"temperature":[float], ...}':
        arr_filtered_by_dt = self.filter_by_dts(from_dt, to_dt)
        arr_filtered_by_metric = self.filter_by_metric(arr_filtered_by_dt, metric)
        return arr_filtered_by_metric 


__cacher = None

def get_cacher():
    #singleton
    global __cacher

    if not __cacher:
        __cacher = Cacher()

    return __cacher
