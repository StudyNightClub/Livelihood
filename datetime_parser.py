import re
from datetime import datetime

def roc_to_common_date(roc_date):
    roc_date_format = re.compile(r'(\d{3})(\d{2})(\d{2})')
    m = roc_date_format.match(roc_date)
    if m:
        year = int(m.group(1)) + 1911
        return '{}-{}-{}'.format(year, m.group(2), m.group(3))
    else:
        return roc_date

def parse_power_date_time(raw_str):
    tokens = re.split('\s|~', raw_str)
    if len(tokens) != 3:
        return (None, None, None)

    event_date = tokens[0].replace('/', '-')
    start_time = tokens[1] + ':00'
    end_time = tokens[2] + ':00'
    return (event_date, start_time, end_time)
