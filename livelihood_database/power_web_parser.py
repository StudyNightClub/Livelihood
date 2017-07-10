# coding=utf-8

from bs4 import BeautifulSoup
import requests
import re
from . import datetime_parser
from . import map_converter

_INFO_REGEX = '([A-Z\da-z]*)(.+)'

_HTML_ADDRESS_REGEX = '(?:\d*)?(?:台灣)?(.*?市)((?:.*?區)?)((?:.*?(?:路|街|大道|橋)(?:[一二三四五六七八九十\d]*?段)?)?)((?:\d*?巷)?(?:\d*?弄)?(?:[-\d]*?號)?)(?:.*)'

info_pattern = re.compile(_INFO_REGEX)
address_pattern = re.compile(_HTML_ADDRESS_REGEX)

def get_html_info(results):
    html_soup = BeautifulSoup(results.text, 'lxml')

    table = html_soup.find_all(class_='PowerCutTable')

    events = []
    for rows in table:
        table_date = rows.caption
        table_content = rows.find_all('td')

        i = 0
        while( i != len(table_content)):

            # start date (end date)
            date_info = get_html_date(table_date.contents[0])

            # start time
            start_time_info = get_html_start_time(table_content[i].contents[0])

            # end time
            end_time_info = get_html_end_time(table_content[i].contents[2])

            # serial number and description
            sn_info, description_info = get_html_serial_number_description(table_content[i+1].contents[0])

            # address and coordinate
            location_info, (latitude, longitude) = get_html_address_coordinate(table_content[i+1].contents[2])

            events.append((
                date_info,
                start_time_info,
                end_time_info,
                sn_info,
                description_info,
                location_info,
                latitude,
                longitude))
            i += 2

    return events

def get_html_date(raw_str_0):
    if raw_str_0:

        # start date (end date)
        date_token = re.sub('\s|停電日期：', '', raw_str_0)
        date_group = re.split('年|月|日', date_token)

        if len(date_group)>=3:
            date_group[1] = date_group[1].zfill(2)
            date_group[2] = date_group[2].zfill(2)
            event_date = datetime_parser.roc_to_common_date(''.join(date_group))

            return event_date
        else:
            print('Unrecognized date: ' + raw_str_0)
            return None

    else:
        print('The date of power event is None')
        return None

def get_html_start_time(raw_str_1):
    if raw_str_1:

        # start time
        start_time_token = re.sub('\s|自', '', raw_str_1)
        start_time_group = re.split('時', start_time_token)

        if len(start_time_group)>=2:
            event_start_time = datetime_parser._process_time(None, start_time_group[0], start_time_group[1])

            return event_start_time
        else:
            print('Unrecognized time format: ' + raw_str_1)
            return None

    else:
        print('The start time of power event is None')
        return None

def get_html_end_time(raw_str_2):
    if raw_str_2:

        # end time
        end_time_token = re.sub('\s|至', '', raw_str_2)
        end_time_group = re.split('時', end_time_token)

        if len(end_time_group)>=2:
            event_end_time = datetime_parser._process_time(None, end_time_group[0], end_time_group[1])

            return event_end_time
        else:
            print('Unrecognized time format: ' + raw_str_2)
            return None

    else:
        print('The end time of power event is None')
        return None

def get_html_serial_number_description(raw_str_3):
    if raw_str_3:
        info_token = re.sub('\s', '', raw_str_3)
        info_token = re.sub('短暫停電', '-短暫停電', info_token)
        info_token = re.sub('\(', '', info_token)
        info_token = re.sub(',因\)|\)', '', info_token)

        info_result = info_pattern.search(info_token)

        if info_result:
            event_serial_number = info_result.groups()[0]
            event_description = info_result.groups()[1]

            return (event_serial_number, event_description)
        else:
            print('Unable to parse description: ' + raw_str_3)
            return (None, None)

    else:
        print('The serial number and description of power event are None')
        return (None, None)

def get_html_address_coordinate(raw_str_4):
    if raw_str_4:
        address_tokens = re.split('，', raw_str_4)

        for address_token in address_tokens:
            address_token = re.sub('‧|、|－|之|至|及', '-', address_token)

            sub_address = address_pattern.search(address_token)

            if sub_address:
                address = ''.join(sub_address.groups())
                coordinate = map_converter.convert_address_to_coordinate(address)

                if coordinate != (None, None):
                    return (sub_address.groups(), coordinate)

        if not sub_address:
            print('Unable to parse address: ' + raw_str_4)
            return ((None, None, None, None), (None, None))

        print('It is failed to convert address to coordinate: ' + address)
        return ((None, None, None, None), coordinate)

    else:
        print('The address of power event is None')
        return ((None, None, None, None), (None, None))
