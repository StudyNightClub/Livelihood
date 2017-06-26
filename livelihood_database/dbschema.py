# encoding: utf-8
import enum
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import FetchedValue
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class EventType(enum.Enum):
    water = 1
    power = 2
    road = 3


class Event(Base):
    __tablename__ = 'event'

    _FIELDS = set(['id', 'gov_sn', 'type', 'city', 'district', 'road',
            'detail_addr', 'start_date', 'end_date', 'start_time', 'end_time',
            'description', 'update_time', 'affected_areas'])

    # columns
    id = Column(String, primary_key=True)
    gov_sn = Column(String)
    type = Column(Enum(EventType))
    city = Column(String)
    district = Column(String)
    road = Column(String)
    detail_addr = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    description = Column(String)
    create_time = Column(DateTime, server_default=FetchedValue())
    update_time = Column(DateTime, server_default=FetchedValue())
    is_active = Column(Boolean)

    # relationships
    coordinates = relationship('Coordinate', back_populates='event')

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
            if len(self.coordinates) == 1:
                shape = 'point'
            else:
                shape = 'polygon'
            coordinates = [a.to_dict() for a in self.coordinates]
            return [{'shape': shape, 'coordinates': coordinates}]
        else:
            return self.__dict__[field]


class Coordinate(Base):
    __tablename__ = 'coordinate'

    # columns
    id = Column(String, primary_key=True)
    wgs84_latitude = Column('latitude', Numeric)
    wgs84_longitude = Column('longitude', Numeric)
    event_id = Column('event_id', String, ForeignKey('event.id'))

    # relationships
    event = relationship('Event', back_populates='coordinates')

    def to_dict(self):
        return {
                   'wgs84_latitude': self.wgs84_latitude,
                   'wgs84_longitude': self.wgs84_longitude
               }
