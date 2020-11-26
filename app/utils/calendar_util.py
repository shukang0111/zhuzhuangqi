from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Tuple


def calc_time(time_str: str) -> Tuple[datetime, datetime]:
    """计算起止时间

    Args:
        time_str: 表示时间段的字符串：
            'today' - 今日，'yesterday' - 昨日，'week' - 本周，'month' - 本月，'last_month' - 上个月，'year' - 今年；
            也可以将起止时间分别以ISO标准时间格式表示，并用'~'连接后传入
    """
    today = date.today()
    year, month, day = today.year, today.month, today.day
    if time_str == 'today':
        start = datetime(year, month, day)
        end = start + timedelta(days=1, microseconds=-1)
    elif time_str == 'yesterday':
        start = datetime(year, month, day) - timedelta(days=1)
        end = start + timedelta(days=1, microseconds=-1)
    elif time_str == 'week':
        start = datetime(year, month, day) - timedelta(days=today.weekday())
        end = start + timedelta(weeks=1, microseconds=-1)
    elif time_str == 'month':
        _, days = monthrange(year, month)
        start = datetime(year, month, 1)
        end = start + timedelta(days=days, microseconds=-1)
    elif time_str == 'last_month':
        if month == 1:
            year, month = year - 1, 12
        else:
            month -= 1
        _, days = monthrange(year, month)
        start = datetime(year, month, 1)
        end = start + timedelta(days=days, microseconds=-1)
    elif time_str == 'year':
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1) + timedelta(microseconds=-1)
    elif time_str == 'seven_day':
        start = datetime(year, month, day) - timedelta(days=7)
        end = datetime(year, month, day) + timedelta(days=1, microseconds=-1)
    elif time_str == 'thirty_day':
        start = datetime(year, month, day) - timedelta(days=30)
        end = datetime(year, month, day) + timedelta(days=1, microseconds=-1)
    else:
        start, end = map(datetime.fromisoformat, time_str.split('~'))
        end = end + timedelta(days=1, microseconds=-1)
        if start > end:
            raise ValueError('The start time is later than the end time')
    return start, end








