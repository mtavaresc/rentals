from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///db.sqlite3')

Session = sessionmaker(bind=engine)

Base = declarative_base()


class Rentals(Base):
    __tablename__ = 'rentals'

    id = Column(Integer, primary_key=True)
    link = Column(String(255))
    bedroom = Column(Integer)
    area = Column(Integer)
    lots = Column(Integer)
    neighbour = Column(String(50))
    condominium = Column(Float(11, 2))
    price = Column(Float(11, 2))
    catch_at = Column(Date, default=date.today(), onupdate=date.today())

    def __init__(self, item, link, bed, area, lots, neighbour, condominium, price):
        self.id = item
        self.link = link
        self.bedroom = bed
        self.area = area
        self.lots = lots
        self.neighbour = neighbour
        self.condominium = condominium
        self.price = price
