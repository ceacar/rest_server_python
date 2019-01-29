from dateutil.parser import parse
import time
from weathertracker.utils.errors import(
    DatetimeConversionException,
    FloatNumberConversionException,
    InvalidTimestampFormatException
)
__EXPECTED_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
__TO_STR_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
__EXAMPLE_TIMESTAMP_INPUT = "2015-09-01T16:00:00.000Z"

def _convert_to_datetime(value):
    try:
        value = parse(value)
    except (ValueError, OverflowError):
        raise DatetimeConversionException()
    return value

def to_datetime(timestamp: 'str: 2015-09-01T16:00:00.000Z'):
    #only allow the expected timestamp format
    if not is_timestamp_utc(timestamp):
        raise InvalidTimestampFormatException("Invalid timestamp:{0}, try something like {1}".format(timestamp, __EXAMPLE_TIMESTAMP_INPUT))
    return _convert_to_datetime(timestamp)

def is_timestamp_utc(timestamp: 'str of timestamp that match __EXPECTED_TIMESTAMP_FORMAT'):
    try:
        time.strptime(timestamp, __EXPECTED_TIMESTAMP_FORMAT)
        return True
    except ValueError:
        return False

def to_timestamp_utc_str(timestamp_dt:'Datetime') -> 'str: 2015-09-01T16:00:00.000Z':
    res = timestamp_dt.strftime(__TO_STR_TIMESTAMP_FORMAT)
    return res[:-3] + "Z" #trim return string format to form desired timeformat

def to_float(num: 'str') -> 'float':
    try:
        res = 0.0
        if num:
            res = float(num)
        return res
    except ValueError:
        raise FloatNumberConversionException("Error converting {0} to float".format(num))

