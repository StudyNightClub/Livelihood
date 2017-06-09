import re

def roc_to_common_date(roc_date):
    roc_date_format = re.compile(r'(\d{3})(\d{2})(\d{2})')
    m = roc_date_format.match(roc_date)
    if m:
        year = int(m.group(1)) + 1911
        return '{}-{}-{}'.format(year, m.group(2), m.group(3))
    else:
        return roc_date
