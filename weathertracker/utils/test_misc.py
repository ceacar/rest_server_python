import unittest
import json
import datetime
import cache
import utils
import misc
import weathertracker
from dateutil.tz import tzutc
from weathertracker.utils.misc import *
from weathertracker.utils.errors import *

class TestMisc(unittest.TestCase):

    def test_parse_json_param(self):
        json_input = {"timestamp":"2015-09-01T16:00:00.000Z", "temperature":"32", "dewPoint": "31", "precipitation": "12"}
        timestamp, temperature, dewPoint, precipitation = parse_json_param(json_input)
        assert timestamp == datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc())
        assert temperature == 32.0
        assert dewPoint == 31.0
        assert precipitation == 12.0
        #rogue timestamp
        json_bad_timestamp_input = {"timestamp":"asdfsdag2015-09-01T16:00:00.000Z", "temperature":"32", "dewPoint": "31", "precipitation": "12"}

        try:
            parse_json_param(json_bad_timestamp_input)
            assert False
        except weathertracker.utils.errors.InvalidTimestampFormatException:
            assert True


        json_bad_number_input = {"timestamp":"2015-09-01T16:00:00.000Z", "temperature":"abc", "dewPoint": "31", "precipitation": "12"}
        try:
            parse_json_param(json_bad_number_input)
            assert False
        except weathertracker.utils.errors.FloatNumberConversionException:
            assert True

        json_empty_number_input = {"timestamp":"2015-09-01T16:00:00.000Z", "temperature":"32", "dewPoint": "31", "precipitation": ""}
        timestamp, temperature, dewPoint, precipitation = parse_json_param(json_empty_number_input)
        assert precipitation == 0.0

    def test_calculate_average(self):
        dew_point_arr = [ 17.1, 17.3]
        res = calculate_average(dew_point_arr)
        assert res == 17.2

    def test_format_stats_result(self):
        metric_dict = {"precipitation": [16.9, 17.6, 17.3], "temperature": [16.9, 17.3, 17.1]}
        stats = ["min", "max", "average"]
        metrics = ["temperature", "precipitation"]
        res = format_stats_result(metric_dict, stats, metrics)
        expected_result = [
            {"metric": "temperature", "stat": "min", "value": 16.9},
            {"metric": "temperature", "stat": "max", "value": 17.3},
            {"metric": "temperature", "stat": "average", "value": 17.1},
            {"metric": "precipitation", "stat": "min", "value": 16.9},
            {"metric": "precipitation", "stat": "max", "value": 17.6},
            {"metric": "precipitation", "stat": "average", "value": 17.3}
        ]
        assert res == json.dumps(expected_result)

    def test_format_stats_result_empty(self):
        """
        Test scenario below(when return is empty)

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
        metric_dict = {"precipitation": []}
        stats = ["min", "max", "average"]
        metrics = ["precipitation"]
        res = format_stats_result(metric_dict, stats, metrics)
        assert res == '[]'

if __name__ == '__main__':
    unittest.main()
