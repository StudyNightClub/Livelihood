from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import dbschema


class DBConnector(object):
    def __init__(self, url):
        self._engine = create_engine(url, echo=True)
        self._Session = sessionmaker(self._engine)

    def create_tables(self):
        dbschema.Base.metadata.create_all(self._engine)

    def get_session(self):
        return self._Session()
