from enum import unique
from sqlalchemy import BLOB, Column, Integer, String, Date
from . import database


# Define App class inheriting from Base
class App(database.Base):
    __tablename__ = 'app'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(265), unique = True)
    description = Column(String)
    image = Column(String(1000))
    location = Column(String(1000))
    language = Column(String(265))