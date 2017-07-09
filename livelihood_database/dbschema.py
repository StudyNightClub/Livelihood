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
    gov_sn = Column(String, nullable=False)
    type = Column(Enum(EventType), nullable=False)
    city = Column(String, nullable=False)
    district = Column(String, nullable=False)
    road = Column(String, nullable=False)
    detail_addr = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    description = Column(String)
    create_time = Column(DateTime, server_default=FetchedValue())
    update_time = Column(DateTime, server_default=FetchedValue())
    is_active = Column(Boolean, nullable=False)

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

    def is_valid(self):
        for c in Event.__table__.columns:
            if not c.nullable and self.__dict__[c.name] is None:
                return False
        return True


class Coordinate(Base):
    __tablename__ = 'coordinate'

    # columns
    id = Column(String, primary_key=True)
    wgs84_latitude = Column('latitude', Numeric, nullable=False)
    wgs84_longitude = Column('longitude', Numeric, nullable=False)
    event_id = Column('event_id', String, ForeignKey('event.id'), nullable=False)

    # relationships
    event = relationship('Event', back_populates='coordinates')

    def to_dict(self):
        return {
                   'wgs84_latitude': self.wgs84_latitude,
                   'wgs84_longitude': self.wgs84_longitude
               }
