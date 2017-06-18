# coding=utf-8

from abc import ABCMeta, abstractmethod
from collections import namedtuple
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
from .dbschema import Event, Area, Coordinate

LDB_URL = os.environ['LDB_URL']

class DataImporter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.connect = DBConnector(LDB_URL)
        self.session = self.connect.get_session()
        self.events = []
        self.groups = []
        self.coordinates = []

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

        self.generate_events(source)
        self._mask_old_entries()
        self._insert_entries()
        self.session.commit()
        self.session.close()

    def _mask_old_entries(self):
        for e in self.session.query(Event)\
                     .filter(Event.update_status == 'new')\
                     .filter(Event.type == self.get_event_type()):
            e.update_status = 'old'

    def _insert_entries(self):
        self.session.add_all(self.events)
        self.session.add_all(self.groups)
        self.session.add_all(self.coordinates)


class WaterImporter(DataImporter):

    _WATER_SOURCE = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=a242ee9b-b954-4ae9-9827-2344c5dfeaea'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return 'water'

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

            description_info = location_parser.parse_water_address(event_water['Description'], 'description')

            for coordinate_group in event_water['StopWaterSection_wgs84']['coordinates']:

                latitude = coordinate_group[0][1]
                longitude = coordinate_group[0][0]

                # Convert coordinate to address
                address = map_converter.convert_coordinate_to_address(latitude, longitude)

                location_info = location_parser.parse_water_address(address, 'location')

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
                    description=description_info[0],
                    update_status='new',
                    update_time=get_current_time()
                )
                self.events.append(event_model)

                group_model = Area(id=get_uuid(), event_id=event_model.id)
                self.groups.append(group_model)
                for coordinate in coordinate_group:
                    coordinate_model = Coordinate(id=get_uuid(),
                                                  wgs84_latitude=coordinate[1],
                                                  wgs84_longitude=coordinate[0],
                                                  area_id=group_model.id)
                    self.coordinates.append(coordinate_model)


class RoadImporter(DataImporter):

    _ROAD_SOURCE = 'http://data.taipei/opendata/datalist/apiAccess?scope=resourceAquire&rid=201d8ae8-dffc-4d17-ae1f-e58d8a95b162'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return 'road'

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
                update_status='new',
                update_time=get_current_time()
            )
            self.events.append(event_model)

            group_model = Area(id=get_uuid(),
                               event_id=event_model.id)
            self.groups.append(group_model)

            coordinate_model = Coordinate(id=get_uuid(),
                                          wgs84_latitude=latitude,
                                          wgs84_longitude=longitude,
                                          area_id=group_model.id)
            self.coordinates.append(coordinate_model)


class PowerImporter(DataImporter):

    _ZIP_FILE = '台灣電力公司_計畫性工作停電資料.zip'
    _POWER_SOURCE = ('http://data.taipower.com.tw/opendata/apply/file/d077004/'
        + urllib.parse.quote(_ZIP_FILE))
    _TEXT_FILE = 'wkotgnews/102.txt'

    def __init__(self):
        super().__init__()

    def get_event_type(self):
        return 'power'

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
            self._get_single_event(event, location_info, timeinfo, coordinate)

            # Second working period
            if event[4] and event[4] != '無':
                timeinfo = datetime_parser.parse_power_date_time(event[4])
                self._get_single_event(event, location_info, timeinfo, coordinate)

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
            update_status='new',
            update_time=get_current_time()
        )
        self.events.append(event_model)

        group_model = Area(id=get_uuid(),
                           event_id=event_model.id)
        self.groups.append(group_model)

        coordinate_model = Coordinate(id=get_uuid(),
                                      wgs84_latitude=float(coordinate[0]),
                                      wgs84_longitude=float(coordinate[1]),
                                      area_id=group_model.id)
        self.coordinates.append(coordinate_model)


### Import all types of livelihood data ###
def import_all():
    WaterImporter().import_data()
    RoadImporter().import_data()
    PowerImporter().import_data()


### Create livelihood database ###
def create_tables():
    connect = DBConnector(LDB_URL)
    connect.create_tables()


def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def get_uuid():
    return str(uuid.uuid4())
