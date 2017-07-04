# coding=utf-8

from bs4 import BeautifulSoup
import requests
import re
import datetime_parser
import map_converter

INFO_REGEX = '([A-Z\da-z]*)(.+)'

_HTML_ADDRESS_REGEX = '(?:\d*)?(?:台灣)?(.*?市)((?:.*?區)?)((?:.*?(?:路|街|大道|橋)(?:[一二三四五六七八九十\d]*?段)?)?)((?:\d*?巷)?(?:\d*?弄)?(?:[-\d]*?號)?)(?:.*)'

info_pattern = re.compile(INFO_REGEX)
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
            event = []
            event.append(table_date.contents[0])      # start date (end date)
            event.append(table_content[i].contents[0])     # start time
            event.append(table_content[i].contents[2])     # end time
            event.append(table_content[i+1].contents[0])       # serial number and description
            event.append(table_content[i+1].contents[2])       # address
            events.append(event)
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
        else:
            event_date = '0000-00-00'
            
        return event_date
        
    else:
        return None

def get_html_start_time(raw_str_1):
    if raw_str_1:
        
        # start time
        start_time_token = re.sub('\s|自', '', raw_str_1)
        start_time_group = re.split('時', start_time_token)
        
        if len(start_time_group)>=2:
            event_start_time = datetime_parser._process_time(None, start_time_group[0], start_time_group[1])
        else:
            event_start_time = '99:99:99'
        
        return event_start_time        
    else:
        return None

def get_html_end_time(raw_str_2):
    if raw_str_2:
        
        # end time
        end_time_token = re.sub('\s|至', '', raw_str_2)
        end_time_group = re.split('時', end_time_token)
        
        if len(end_time_group)>=2:
            event_end_time = datetime_parser._process_time(None, end_time_group[0], end_time_group[1])
        else:
            event_end_time = '99:99:99'
        
        return event_end_time        
    else:
        return None

def get_html_date_time(raw_str_0, raw_str_1, raw_str_2):
    return (get_html_date(raw_str_0), get_html_start_time(raw_str_1), get_html_end_time(raw_str_2))

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
            return ('000000', 'null')
            
    else:
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
                
                if coordinate != (25.027223, 121.5764989):
                    return (sub_address.groups(), coordinate)
        
        if not sub_address:
            return (('null', 'null', 'null', 'null'), (25.027223, 121.5764989))
        
        return (('市', '區', '路', '象山'), coordinate)
        
    else:
        return ((None, None, None, None), (None, None))


# """ Log for testing """
# def get_raw_data():
    # _POWER_SOURCE = 'http://branch.taipower.com.tw/Content/NoticeBlackout/bulletin.aspx?SiteID=564732646551216421&MmmID=616371300113254267'
    
    # response = requests.get(_POWER_SOURCE)
    
    # if response.status_code == 200:
        # print('Web (POWER OUTAGE) request is ok.')
        # return response
    # else:
        # print('Web (POWER OUTAGE) request is NOT ok. Response status code = %s.' % response.status_code)
        # return None

# for event_power in get_html_info(get_raw_data()):
    # datetime = get_html_date_time(event_power[0], event_power[1], event_power[2])
    # print(datetime)    
    
    # sn_info, description_info = get_html_serial_number_description(event_power[3])
    # print(sn_info, description_info)
    
    # address, (latitude, longitude) = get_html_address_coordinate(event_power[4])
    # print(address[0], address[1], address[2], address[3])
    # print(latitude, longitude)
