from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    english_name = Column(String(255), nullable=False)
    korean_name = Column(String(255), nullable=True)
    country_code = Column(String(10), nullable=True)
    country_eng = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
