# encoding: utf-8
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = 'event'

    _FIELDS = set(['id', 'gov_sn', 'type', 'city', 'district', 'road',
            'detail_addr', 'start_date', 'end_date', 'start_time', 'end_time',
            'description', 'update_time', 'affected_areas'])

    # columns
    id = Column('event_id', String, primary_key=True)
    gov_sn = Column('gov_serial_number', String)
    type = Column('event_type', String)
    city = Column(String)
    district = Column(String)
    road = Column('road_street_boulevard_section', String)
    detail_addr = Column('lane_alley_number', String)
    start_date = Column(String)
    end_date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    description = Column(String)
    update_time = Column(String)
    update_status = Column(String)

    # relationships
    areas = relationship('Area', back_populates='event')

    def to_dict(self, fields=None):
        if fields:
            fields = set(filter(self._FIELDS.__contains__, fields))
            fields.add('id')
        else:
            fields = list(self._FIELDS)

        result = {}
        for f in fields:
            result[f] = self.get_field(f)
        return result

    def get_field(self, field):
        if field == 'affected_areas':
            return [a.to_dict() for a in self.areas]
        else:
            return self.__dict__[field]

class Area(Base):
    __tablename__ = 'event_coord_group'

    # columns
    id = Column('group_id', String, primary_key=True)
    event_id = Column(String, ForeignKey('event.event_id'))

    # relationships
    event = relationship('Event', back_populates='areas')
    coordinates = relationship('Coordinate', back_populates='area')

    def to_dict(self):
        return {
                   'shape': 'point' if len(self.coordinates) == 1 else 'polygon',
                   'coordinates': [c.to_dict() for c in self.coordinates]
               }

class Coordinate(Base):
    __tablename__ = 'event_coordinate'

    # columns
    id = Column('coordinate_id', String, primary_key=True)
    wgs84_latitude = Column('latitude', Float)
    wgs84_longitude = Column('longitude', Float)
    area_id = Column('group_id', String, ForeignKey('event_coord_group.group_id'))

    # relationships
    area = relationship('Area', back_populates='coordinates')

    def to_dict(self):
        return {
                   'wgs84_latitude': self.wgs84_latitude,
                   'wgs84_longitude': self.wgs84_longitude
               }
