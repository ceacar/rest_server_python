class DatetimeConversionException(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class FloatNumberConversionException(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class InvalidTimestampFormatException(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class InvalidMetricException(Exception):
    def __init__(self, message):
        self.message = message + "\n"

class NoStatsException(Exception):
    def __init__(self, message):
        self.message = message + "\n"

