# coding=utf-8

from enum import Enum
import requests
import urllib.request
import urllib.parse
import zipfile
import sqlite3
import time
import uuid

import convert
import datetime_parser


class EventType(Enum):
    WATER = 'water'
    ROAD = 'road'
    POWER = 'power'


### Import all types of livelihood data ###
def import_all_types_data(database_filename):
    import_data(database_filename, EventType.WATER)
    import_data(database_filename, EventType.ROAD)
    import_data(database_filename, EventType.POWER)

### Import livelihood data ###
def import_data(database_filename, type_enum_name):
    
    ### WATER OUTAGE ###
    if type_enum_name == EventType.WATER:
        print('test')
        url_water = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=a242ee9b-b954-4ae9-9827-2344c5dfeaea'
        
        web_request_water = requests.get(url_water)     # Request
        
        if web_request_water.status_code == 200:
            print('Web (WATER OUTAGE) request is ok.')
            
            json_water = web_request_water.json()
            
            connect = sqlite3.connect(database_filename)
            conn = connect.cursor()   
            
            # update data status
            conn.execute("""UPDATE event SET update_status = 'old' 
                WHERE event_type = 'water' AND update_status = 'new'""")
            
            # arrange data and insert to table
            events_water = []
            groups_water = []
            coordinates_water = []            
            for event_water in json_water['result']['results']:

                timeinfo = datetime_parser.parse_water_road_time(event_water['Description'])
                
                content_event = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    'water', 
                    event_water['SW_No'], 
                    '台北市', 
                    event_water['SW_Area'], 
                    event_water['SW_Area'], 
                    event_water['SW_Area'], 
                    datetime_parser.roc_to_common_date(event_water['FS_Date']), 
                    datetime_parser.roc_to_common_date(event_water['FC_Date']), 
                    timeinfo[0], 
                    timeinfo[1], 
                    event_water['Description'], 
                    'new', 
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                events_water.append(content_event)
                    
                content_group = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    content_event[0])
                groups_water.append(content_group)
                
                for coordinate_water in event_water['StopWaterSection_wgs84']['coordinates']:       
                    for coordinate in coordinate_water:            
                        content_coordinate = (
                            (str(uuid.uuid1())[0:23]).replace('-', ''), 
                            coordinate[1], 
                            coordinate[0], 
                            content_group[0])
                        coordinates_water.append(content_coordinate)
            
            conn.executemany("""INSERT INTO event 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", events_water)
            conn.executemany("""INSERT INTO event_coord_group(
                group_id, 
                event_id) 
                VALUES (?,?)""", groups_water)
            conn.executemany("""INSERT INTO event_coordinate(
                coordinate_id, 
                latitude, 
                longitude, 
                group_id) 
                VALUES (?,?,?,?)""", coordinates_water)
            
            connect.commit()
            connect.close()            
        else:
            print('Web (WATER OUTAGE) request is NOT ok. Request status code = %s.' 
                %(web_request_water.status_code))
    
    ### ROAD CONSTRUCTION ###
    elif type_enum_name == EventType.ROAD:
        url_road = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=201d8ae8-dffc-4d17-ae1f-e58d8a95b162'
        
        web_request_road = requests.get(url_road)     # Request
        
        if web_request_road.status_code == 200:
            print('Web (ROAD CONSTRUCTION) request is ok.')
            
            json_road = web_request_road.json()
            
            connect = sqlite3.connect(database_filename)
            conn = connect.cursor()
            
            # update data status
            conn.execute("""UPDATE event SET update_status = 'old' 
                WHERE event_type = 'road' AND update_status = 'new'""")
            
            # arrange data and insert to table
            events_road = []
            groups_road = []
            coordinates_road = []
            for event_road in json_road['result']['results']:

                timeinfo = datetime_parser.parse_water_road_time(event_road['CO_TI'])
                
                content_event = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    'road', 
                    '#'.join((event_road['AC_NO'], event_road['SNO'])), 
                    '台北市', 
                    event_road['C_NAME'], 
                    event_road['ADDR'], 
                    event_road['ADDR'], 
                    datetime_parser.roc_to_common_date(event_road['CB_DA']),
                    datetime_parser.roc_to_common_date(event_road['CE_DA']),
                    timeinfo[0],
                    timeinfo[1],
                    event_road['NPURP'], 
                    'new', 
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                events_road.append(content_event)
                
                content_group = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    content_event[0])
                groups_road.append(content_group)
                
                # Convert TWD97 to WGS84
                latitude_road, longitude_road = convert.twd97_to_wgs84(float(event_road['X']), float(event_road['Y']))
                
                content_coordinate = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    latitude_road, 
                    longitude_road, 
                    content_group[0])
                coordinates_road.append(content_coordinate)

            conn.executemany("""INSERT INTO event 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", events_road)
            conn.executemany("""INSERT INTO event_coord_group(
                group_id, 
                event_id) 
                VALUES (?,?)""", groups_road)
            conn.executemany("""INSERT INTO event_coordinate(
                coordinate_id, 
                latitude, 
                longitude, 
                group_id) 
                VALUES (?,?,?,?)""", coordinates_road)
               
            connect.commit()
            connect.close()            
        else:
            print('Web (ROAD CONSTRUCTION) request is NOT ok. Request status code = %s.' 
                %(web_request_road.status_code))        
    
    ### POWER OUTAGE ###
    elif type_enum_name == EventType.POWER:
        filename_power = '台灣電力公司_計畫性工作停電資料.zip'
        url_power = ('http://data.taipower.com.tw/opendata/apply/file/d077004/' 
            + urllib.parse.quote(filename_power))
        txt_name_power = 'wkotgnews/102.txt'
        
        # Download file
        urllib.request.urlretrieve(url_power, filename_power)

        if urllib.request.urlretrieve != None:
            print('Download (POWER OUTAGE) file is ok.')
            
            # Unzip downloaded file
            zip_power = zipfile.ZipFile(filename_power)
            file_power = zip_power.extract(txt_name_power)
            print('Unzipped (POWER OUTAGE) file is "%s".' %file_power)
            zip_power.close()

            # Read the content of txt file
            txt_file_power = open(txt_name_power, 'r')
            lines_power = txt_file_power.readlines()

            line_power = []
            txt_power = []
            for line in lines_power[1:]:
                line_adapted_power = line.strip()
                line_power = line_adapted_power.split('#')
                txt_power.append(line_power)
            txt_file_power.close()
            
            connect = sqlite3.connect(database_filename)
            conn = connect.cursor()
            
            # update data status
            conn.execute("""UPDATE event SET update_status = 'old' 
                WHERE event_type = 'power' AND update_status = 'new'""")
                
            # arrange data and insert to table
            events_power = []
            groups_power = []
            coordinates_power = []
            for event_power in txt_power:    
                # Convert Address to coordinate
                coordinate_power = convert.address_to_coordinate(event_power[5])
                
                # First working period
                timeinfo_first_period = datetime_parser.parse_power_date_time(event_power[3])
                content_event_first_period = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    'power', 
                    event_power[1], 
                    '台北市', 
                    event_power[5],
                    event_power[5],
                    event_power[5],
                    timeinfo_first_period[0],
                    timeinfo_first_period[0],
                    timeinfo_first_period[1],
                    timeinfo_first_period[2],
                    event_power[2],
                    'new', 
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                events_power.append(content_event_first_period)
                
                content_group_first_period = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    content_event_first_period[0])
                groups_power.append(content_group_first_period)
                
                content_coordinate_first_period = (
                    (str(uuid.uuid1())[0:23]).replace('-', ''), 
                    float(coordinate_power[0]), 
                    float(coordinate_power[1]), 
                    content_group_first_period[0])
                coordinates_power.append(content_coordinate_first_period)
                
                # Second working period
                if event_power[4] != '無':
                    timeinfo_second_period = datetime_parser.parse_power_date_time(event_power[4])
                    content_event_second_period = (
                        (str(uuid.uuid1())[0:23]).replace('-', ''), 
                        'power', 
                        event_power[1], 
                        '台北市', 
                        event_power[5],
                        event_power[5],
                        event_power[5],
                        timeinfo_second_period[0],
                        timeinfo_second_period[0],
                        timeinfo_second_period[1],
                        timeinfo_second_period[2],
                        event_power[2],
                        'new', 
                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
                    events_power.append(content_event_second_period)
                
                    content_group_second_period = (
                        (str(uuid.uuid1())[0:23]).replace('-', ''), 
                        content_event_second_period[0])
                    groups_power.append(content_group_second_period)
                    
                    content_coordinate_sceond_period = (
                        (str(uuid.uuid1())[0:23]).replace('-', ''), 
                        float(coordinate_power[0]), 
                        float(coordinate_power[1]), 
                        content_group_second_period[0])
                    coordinates_power.append(content_coordinate_sceond_period)

            conn.executemany("""INSERT INTO event 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", events_power)
               
            conn.executemany("""INSERT INTO event_coord_group(
                group_id, 
                event_id) 
                VALUES (?,?)""", groups_power)
               
            conn.executemany("""INSERT INTO event_coordinate(
                coordinate_id, 
                latitude, 
                longitude, 
                group_id) 
                VALUES (?,?,?,?)""", coordinates_power)

            connect.commit()
            connect.close()
        else:
            print('Download (POWER OUTAGE) file is NOT ok.')

    else:
        print('Wrong type name of enum.')


### Create livelihood database ###
def create_database(database_filename):
    
    # Connect database
    connect = sqlite3.connect(database_filename)
    conn = connect.cursor()


    # Create event table
    conn.execute("""CREATE TABLE event(
        event_id TEXT NOT NULL PRIMARY KEY, 
        event_type TEXT NOT NULL, 
        gov_serial_number TEXT NOT NULL, 
        city TEXT, 
        district TEXT, 
        road_street_boulevard_section TEXT, 
        lane_alley_number TEXT , 
        start_date TEXT NOT NULL, 
        end_date TEXT NOT NULL, 
        start_time TEXT, 
        end_time TEXT, 
        description TEXT, 
        update_status TEXT NOT NULL, 
        update_time TEXT NOT NULL)""")

    # Create group table
    conn.execute("""CREATE TABLE event_coord_group(
        group_id TEXT NOT NULL PRIMARY KEY, 
        event_id TEXT NOT NULL, 
        
        FOREIGN KEY(event_id) 
            REFERENCES event(event_id))""")

    # Create coordinate table
    conn.execute("""CREATE TABLE event_coordinate(
        coordinate_id TEXT NOT NULL PRIMARY KEY, 
        latitude REAL NOT NULL, 
        longitude REAL NOT NULL, 
        group_id TEXT NOT NULL, 
        
        FOREIGN KEY(group_id) 
            REFERENCES event_coord_group(group_id))""")

    # Save (commit) the changes and close the connection
    connect.commit()
    connect.close()


