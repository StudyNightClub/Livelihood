# coding=utf-8

from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime, timezone, timedelta
import os
import shutil
import time
import urllib.parse
import uuid
import zipfile
import requests

from . import map_converter
from . import datetime_parser
from . import location_parser
from .dbconnector import DBConnector
from .dbschema import Event, Coordinate, EventType

LDB_URL = os.environ['LDB_URL']
TZ = timezone(timedelta(hours=8))

class DataImporter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.connect = DBConnector(LDB_URL)
        self.session = self.connect.get_session()

    @abstractmethod
    def get_event_type(self):
        pass

    @abstractmethod
    def get_raw_data(self):
        pass

    @abstractmethod
    def generate_events(self, source):
        pass

    def import_data(self):
        source = self.get_raw_data()
        if not source:
            return

        self._set_events_inactive()

        for e in self.generate_events(source):
            self._insert_entry(e)

        self.session.commit()
        self.session.close()

    def _set_events_inactive(self):
        for e in self.session.query(Event)\
                .filter(Event.type == self.get_event_type())\
                .filter(Event.is_active == True):
            e.is_active = False

    def _insert_entry(self, e):
        with self.session.no_autoflush:
            existed = self.session.query(Event)\
                    .filter(Event.gov_sn == e.gov_sn)\
                    .filter(Event.type == e.type)\
                    .filter(Event.city == e.city)\
                    .filter(Event.district == e.district)\
                    .filter(Event.road == e.road)\
                    .filter(Event.detail_addr == e.detail_addr)\
                    .filter(Event.start_date == e.start_date)\
                    .filter(Event.end_date == e.end_date)\
                    .filter(Event.start_time == e.start_time)\
                    .filter(Event.end_time == e.end_time)\
                    .filter(Event.description == e.description)\
                    .first()
            if existed:
                existed.update_time = datetime.now(TZ)
                existed.is_active = True
            else:
                e.update_time = e.create_time = datetime.now(TZ)
                e.is_active = True
                self.session.add(e)


class WaterImporter(DataImporter):

    _WATER_SOURCE = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=a242ee9b-b954-4ae9-9827-2344c5dfeaea'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return EventType.water

    def get_raw_data(self):
        response = requests.get(self._WATER_SOURCE)
        if response.status_code == 200:
            print('Web (WATER OUTAGE) request is ok.')
            return response.json()
        else:
            print('Web (WATER OUTAGE) request is NOT ok. Response status code = %s.'
                %(response.status_code))
            return None

    def generate_events(self, source):
        for event_water in source['result']['results']:
            timeinfo = datetime_parser.parse_water_road_time(event_water['Description'])
            coordinates = event_water['StopWaterSection_wgs84']['coordinates'][0]

            # Convert coordinate to address
            latitude = coordinates[0][1]
            longitude = coordinates[0][0]
            address = map_converter.convert_coordinate_to_address(latitude, longitude)

            location_info = location_parser.parse_water_address(address)

            event_model = Event(
                id=get_uuid(),
                type=self.get_event_type(),
                gov_sn=event_water['SW_No'],
                city=location_info[0],
                district=location_info[1],
                road=location_info[2],
                detail_addr=location_info[3],
                start_date=datetime_parser.roc_to_common_date(event_water['FS_Date']),
                end_date=datetime_parser.roc_to_common_date(event_water['FC_Date']),
                start_time=timeinfo[0],
                end_time=timeinfo[1],
                description=event_water['Description'],
            )
            for coor in coordinates:
                event_model.coordinates.append(Coordinate(id=get_uuid(),
                            wgs84_latitude=coor[1],
                            wgs84_longitude=coor[0]))
            yield event_model


class RoadImporter(DataImporter):

    _ROAD_SOURCE = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=201d8ae8-dffc-4d17-ae1f-e58d8a95b162'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return EventType.road

    def get_raw_data(self):
        response = requests.get(self._ROAD_SOURCE)
        if response.status_code == 200:
            print('Web (ROAD CONSTRUCTION) request is ok.')
            return response.json()
        else:
            print('Web (ROAD CONSTRUCTION) request is NOT ok. Response status code = %s.'
                %(response.status_code))
            return None

    def generate_events(self, source):
        for event in source['result']['results']:
            timeinfo = datetime_parser.parse_water_road_time(event['CO_TI'])

            # Convert TWD97 to WGS84
            latitude, longitude = map_converter.twd97_to_wgs84(float(event['X']), float(event['Y']))

            # Convert coordinate to address
            address = map_converter.convert_coordinate_to_address(latitude, longitude)

            location_info = location_parser.parse_road_address(address)

            event_model = Event(
                id=get_uuid(),
                type=self.get_event_type(),
                gov_sn='#'.join((event['AC_NO'], event['SNO'])),
                city=location_info[0],
                district=location_info[1],
                road=location_info[2],
                detail_addr=location_info[3],
                start_date=datetime_parser.roc_to_common_date(event['CB_DA']),
                end_date=datetime_parser.roc_to_common_date(event['CE_DA']),
                start_time=timeinfo[0],
                end_time=timeinfo[1],
                description=event['NPURP'],
            )
            event_model.coordinates.append(Coordinate(id=get_uuid(),
                        wgs84_latitude=latitude,
                        wgs84_longitude=longitude))
            yield event_model


class PowerImporter(DataImporter):

    _ZIP_FILE = '台灣電力公司_計畫性工作停電資料.zip'
    _POWER_SOURCE = ('http://data.taipower.com.tw/opendata/apply/file/d077004/'
        + urllib.parse.quote(_ZIP_FILE))
    _TEXT_FILE = 'wkotgnews/102.txt'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return EventType.power

    def get_raw_data(self):
        # Download file
        response = requests.get(self._POWER_SOURCE, stream=True)
        if response.status_code == 200:
            with open(self._ZIP_FILE, 'wb') as fout:
                shutil.copyfileobj(response.raw, fout)
        else:
            print('Download (POWER OUTAGE) file is NOT ok.')
            return

        # Unzip downloaded file
        with zipfile.ZipFile(self._ZIP_FILE) as zip_power:
            file_power = zip_power.extract(self._TEXT_FILE)
            print('Unzipped (POWER OUTAGE) file is "%s".' %file_power)

        # Read the content of txt file
        with open(self._TEXT_FILE, 'r') as fin:
            lines = fin.readlines()

        return [line.strip().split('#') for line in lines[1:]]

    def generate_events(self, source):
        # arrange data and insert to table
        for event in source:
            # Convert address to coordinate
            coordinate = map_converter.convert_address_to_coordinate(event[5])
            location_info = location_parser.parse_power_address(event[5])

            # First working period
            timeinfo = datetime_parser.parse_power_date_time(event[3])
            yield self._get_single_event(event, location_info, timeinfo, coordinate)

            # Second working period
            if event[4] and event[4] != '無':
                timeinfo = datetime_parser.parse_power_date_time(event[4])
                yield self._get_single_event(event, location_info, timeinfo, coordinate)

    def _get_single_event(self, line, location_info, timeinfo, coordinate):
        event_model = Event(
            id=get_uuid(),
            type=self.get_event_type(),
            gov_sn=line[1],
            city='台'+str(location_info[0]),
            district=location_info[1],
            road=location_info[2],
            detail_addr=location_info[3],
            start_date=timeinfo[0],
            end_date=timeinfo[0],
            start_time=timeinfo[1],
            end_time=timeinfo[2],
            description=line[2],
        )
        event_model.coordinates.append(Coordinate(id=get_uuid(),
            wgs84_latitude=float(coordinate[0]),
            wgs84_longitude=float(coordinate[1])))
        return event_model


### Import all types of livelihood data ###
def import_all():
    WaterImporter().import_data()
    RoadImporter().import_data()
    PowerImporter().import_data()


### Create livelihood database ###
def create_tables():
    connect = DBConnector(LDB_URL)
    connect.create_tables()


def get_uuid():
    return str(uuid.uuid4())
