import re
from datetime import datetime, date, time

def roc_to_common_date(roc_date):
    roc_date_format = re.compile(r'(\d{3})(\d{2})(\d{2})')
    m = roc_date_format.match(roc_date)
    if m:
        year = int(m.group(1)) + 1911
        return date(year=year, month=int(m.group(2)), day=int(m.group(3)))
    else:
        return None

def parse_water_road_time(raw_str):
    if raw_str:
        raw_str = re.sub(':', '時', raw_str)
        match = parse_water_road_time.pattern.search(raw_str)
    else:
        match = None

    if match:
        start = _process_time(match.group(1), match.group(2), match.group(3))
        end = _process_time(match.group(4), match.group(5), match.group(6))
        return (start, end)
    else:
        return (None, None)

# static object
parse_water_road_time.pattern = re.compile('(上午|下午|中午|傍晚|晚上|晚間|凌晨|翌日)?(\d+時?)(\d+分?)?(?:至|-).*?(上午|下午|中午|傍晚|晚上|晚間|凌晨|翌日)?(\d+時?)(\d+分?)?')

def _process_time(prefix, hour, minute):
    if hour:
        h = int(hour.replace('時', ''))
    else:
        h = 0

    if minute:
        m = int(minute.replace('分', ''))
    else:
        m = 0

    if prefix == '下午' or prefix == '傍晚' or prefix == '晚上' or prefix == '晚間':
        if h == 0:
            h = 12
        elif prefix == '下午' and h == 12:
            h = 0
        h = h + 12

    if h == 24:
        h = 0

    return time(hour=h, minute=m, second=0)

