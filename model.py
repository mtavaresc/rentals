from datetime import date

from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from base import Base, Session

session = Session()


class Rentals(Base):
    __tablename__ = 'rentals'

    id = Column(Integer, primary_key=True)
    link = Column(String(255))
    bedroom = Column(Integer)
    area = Column(Integer)
    lots = Column(Integer)
    neighbour = Column(String(50))
    price = Column(Float(11, 2))
    condominium = Column(Float(11, 2))
    total = Column(Float(11, 2))
    favorite = Column(Boolean, default=False)
    catch_at = Column(Date, default=date.today(), onupdate=date.today())

    def __init__(self, item, link, bed, area, lots, neighbour, condominium, price, total):
        self.id = item
        self.link = link
        self.bedroom = bed
        self.area = area
        self.lots = lots
        self.neighbour = neighbour
        self.condominium = condominium
        self.price = price
        self.total = total

    @staticmethod
    def clean():
        session.query(Rentals).filter_by(favorite=False).delete()
        session.commit()
