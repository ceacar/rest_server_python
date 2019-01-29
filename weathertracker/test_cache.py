import unittest
import datetime
import cache
import utils
import misc
from dateutil.tz import tzutc

class TestCacher(unittest.TestCase):

    def setup_test(self) -> 'cacher instance':
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
            timestamp, temperature, dewPoint, precipitation = misc.parse_json_param(data)
            cacher.save(timestamp, temperature, dewPoint, precipitation)

        return cacher


    def test_cacher_save(self):
        cacher = self.setup_test()
        expected_metric = {
            datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc()), 28.1, 18.3, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 30, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 30, tzinfo=tzutc()), 27.4, 17.3, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()), 27.3, 0.0, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()), 27.5, 17.1, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()), 27.2, 0.0, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc()), 27.1, 16.9, 0.0)}

        assert cacher.temperature_metric == expected_metric

    def test_cacher_get(self):

        cacher = self.setup_test()
        key = datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc())
        expected_dt_entry = (datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc()), 27.1, 16.9, 0.0)

        assert cacher.get(key) ==  expected_dt_entry

        #try to get a non exist
        key = datetime.datetime(2015, 9, 1, 18, 20, tzinfo=tzutc())

        assert cacher.get(key) == None


    def test_cacher_delete(self):
        key = datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc())
        cacher = self.setup_test()
        cacher.delete(key)
        expected_metric_after_del = {
            datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc()), 28.1, 18.3, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 30, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 30, tzinfo=tzutc()), 27.4, 17.3, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()), 27.3, 0.0, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()), 27.5, 17.1, 0.0), 
            datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()), 27.2, 0.0, 0.0), 
        }

        assert cacher.temperature_metric == expected_metric_after_del

    def test_cacher_select(self):
        cacher = self.setup_test()
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
        from_dt = datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc())
        to_dt = datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc())
        metrics = ["temperature"]
        res = cacher.select(from_dt, to_dt, metrics)
        assert res == {'temperature': sorted([27.4, 27.2, 27.1, 27.5, 27.3])}

    def test_cacher_select_2(self):
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

        cacher = self.setup_test()
        cacher.temperature_metric = {
            datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc()), 27.1, 16.9, 0.0),
            datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 10, tzinfo=tzutc()), 27.3, 0.0, 0.0),
            datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 20, tzinfo=tzutc()), 27.5, 17.1, 0.0),
            datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 16, 40, tzinfo=tzutc()), 27.4, 17.3, 0.0),
            datetime.datetime(2015, 9, 1, 17, 00, tzinfo=tzutc()): (datetime.datetime(2015, 9, 1, 17, 00, tzinfo=tzutc()), 28.1, 18.3, 0.0),
        }
        from_dt = datetime.datetime(2015, 9, 1, 16, 0, tzinfo=tzutc())
        to_dt = datetime.datetime(2015, 9, 1, 17, 0, tzinfo=tzutc())
        stats = ["min", "max", "average"]
        metrics = ["dewPoint"]
        res = cacher.select(from_dt, to_dt, metrics)
        assert res == {"dewPoint":sorted([16.9, 0.0, 17.1, 17.3])}

if __name__ == '__main__':
    unittest.main()
