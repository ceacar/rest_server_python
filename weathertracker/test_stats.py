import unittest
import json
from weathertracker.stats import(
    calculate_stat,
    get_stats,
)
from weathertracker.utils.misc import(
    parse_json_param,
)

from weathertracker.utils.conversion import (
    to_datetime,
)

from weathertracker import cache

class TestStat(unittest.TestCase):
    def test_calculate_stat(self):
        """
              | param        | value                    |
              | stat         | min                      |
              | stat         | max                      |
              | stat         | average                  |
              | metric       | temperature              |
              | fromDateTime | 2015-09-01T16:00:00.000Z |
              | toDateTime   | 2015-09-01T17:00:00.000Z |
            Then the response has a status code of 200
            And the response body is an array of:
              | metric        | stat      | value |
              | "temperature" | "min"     | 27.1  |
              | "temperature" | "max"     | 27.5  |
              | "temperature" | "average" | 27.3  |

        """

        metric_res_dict = {'temperature': sorted([27.4, 27.2, 27.1, 27.5, 27.3])}
        assert calculate_stat(metric_res_dict, ["min", "max", "average"]) == {'temperature': [27.1, 27.5, 27.3]}

    def test_calculate_stat2(self):
        """
            | timestamp                  | temperature | dewPoint |
            | "2015-09-01T16:00:00.000Z" | 27.1        | 16.9     |
            | "2015-09-01T16:10:00.000Z" | 27.3        |          |
            | "2015-09-01T16:20:00.000Z" | 27.5        | 17.1     |
            | "2015-09-01T16:30:00.000Z" | 27.4        | 17.3     |
            | "2015-09-01T16:40:00.000Z" | 27.2        |          |
            | "2015-09-01T17:00:00.000Z" | 28.1        | 18.3     |
          ✔ When I get stats with parameters:
            | param        | value                    |
            | stat         | min                      |
            | stat         | max                      |
            | stat         | average                  |
            | metric       | dewPoint                 |
            | fromDateTime | 2015-09-01T16:00:00.000Z |
            | toDateTime   | 2015-09-01T17:00:00.000Z |
          ✔ Then the response has a status code of 200
          ✘ And the response body is an array of:
            | metric     | stat      | value |
            | "dewPoint" | "min"     | 16.9  |
            | "dewPoint" | "max"     | 17.3  |
            | "dewPoint" | "average" | 17.1  |
        """

        metric_res_dict = {'dewPoint': sorted([16.9, 0.0, 17.1, 17.3, 0.0])}
        assert calculate_stat(metric_res_dict, ["min", "max", "average"]) == {'dewPoint': [16.9, 17.3, 17.1]}

    def test_calculate_stat3(self):
        """
        ✘ Scenario: Get stats for a metric that has never been reported
          ✔ Given I have submitted new measurements as follows:
            | timestamp                  | temperature | dewPoint |
            | "2015-09-01T16:00:00.000Z" | 27.1        | 16.9     |
            | "2015-09-01T16:10:00.000Z" | 27.3        |          |
            | "2015-09-01T16:20:00.000Z" | 27.5        | 17.1     |
            | "2015-09-01T16:30:00.000Z" | 27.4        | 17.3     |
            | "2015-09-01T16:40:00.000Z" | 27.2        |          |
            | "2015-09-01T17:00:00.000Z" | 28.1        | 18.3     |
          ✔ When I get stats with parameters:
            | param        | value                    |
            | stat         | min                      |
            | stat         | max                      |
            | stat         | average                  |
            | metric       | precipitation            |
            | fromDateTime | 2015-09-01T16:00:00.000Z |
            | toDateTime   | 2015-09-01T17:00:00.000Z |

        """

        metric_res_dict = {'precipitation': []}
        assert calculate_stat(metric_res_dict, ["min", "max", "average"]) == {'precipitation': []}

    def test_get_stats(self):
        #test empty load
        res = get_stats(["min", "max", "value"], ["temperature", "dewPoint"], '2015-09-01T16:00:00.000Z', '2015-09-01T17:00:00.000Z')
        assert res == ('[]', 200)

        #load data
        data_input_arr = [
            {"timestamp": "2015-09-01T16:00:00.000Z", "temperature": "27.1", "dewPoint": "16.9", "precipitation":"",},
            {"timestamp": "2015-09-01T16:10:00.000Z", "temperature": "27.3", "dewPoint":"","precipitation":"",},
            {"timestamp": "2015-09-01T16:20:00.000Z", "temperature": "27.5", "dewPoint":"17.1","precipitation":"",},
            {"timestamp": "2015-09-01T16:30:00.000Z", "temperature": "27.4", "dewPoint":"17.3","precipitation":"",},
            {"timestamp": "2015-09-01T16:40:00.000Z", "temperature": "27.2", "dewPoint":"","precipitation":"",},
            {"timestamp": "2015-09-01T17:00:00.000Z", "temperature": "28.1", "dewPoint":"18.3","precipitation":""},
        ]

        cacher = cache.get_cacher()

        for data in data_input_arr:
            timestamp, temperature, dewPoint, precipitation = parse_json_param(data)
            cacher.save(timestamp, temperature, dewPoint, precipitation)

        res = get_stats(["min", "max", "average"], ["temperature", "dewPoint"], to_datetime('2015-09-01T16:00:00.000Z'), to_datetime('2015-09-01T17:00:00.000Z'))

        exp_arr =sorted([{"stat": "min", "metric": "temperature", "value": 27.1}, {"stat": "max", "metric": "temperature", "value": 27.5},
                          {"stat": "average", "metric": "temperature","value":27.3},{"stat": "min", "metric": "dewPoint", "value": 16.9},
                          {"stat": "max", "metric": "dewPoint", "value": 17.3}, {"stat": "average", "metric": "dewPoint", "value": 17.1}], key=lambda x:sorted(x.keys()))
        expected_res = (json.dumps(exp_arr), 200)

        assert res == expected_res


if __name__ == '__main__':
    unittest.main()
