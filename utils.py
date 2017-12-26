from datetime import timedelta, datetime
import time

import os
from dateutil import tz

from conf import UNIX_HOUR_REPRESENTATION


def get_day_range_unix_time(days_before_today):
    today = datetime.utcnow().date()
    start_date_time = datetime(today.year, today.month, today.day, tzinfo=tz.tzutc()) - timedelta(days_before_today)
    start_unix = str(int(time.mktime(start_date_time.timetuple())))
    end_date_time = start_date_time + timedelta(1)
    end_unix = str(int(time.mktime(end_date_time.timetuple())))
    return (start_unix, end_unix)


def file_modified_in_last_hour(file_path):
    last_modified_time = os.stat(file_path).st_mtime
    now = time.time()
    unix_time_passed = now - last_modified_time
    return unix_time_passed < UNIX_HOUR_REPRESENTATION
