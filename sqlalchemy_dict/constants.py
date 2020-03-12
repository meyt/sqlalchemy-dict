import re

ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_DATETIME_PATTERN = re.compile(
    r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?:\.(\d*))?(Z|\+\d{2}:\d{2})?$"
)
ISO_DATE_FORMAT = "%Y-%m-%d"
ISO_TIME_FORMAT = "%H:%M:%S"
