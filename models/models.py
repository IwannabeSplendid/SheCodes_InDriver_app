# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Time, Date, Float, Enum, func
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum

from src.database import Base


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(100))
    phone_number = Column(String)
    
    rides = relationship("RideModel", back_populates="client")


class ScheduleModel(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    
    driver = relationship("DriverModel", back_populates="schedules")


class DriverModel(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    license_number = Column(String)
    contact_number = Column(String)
    is_available_now = Column(Boolean, default=True)
    
    car = relationship("CarModel", uselist=False, back_populates="driver")
    schedules = relationship("ScheduleModel", uselist=True, back_populates="driver")
    rides = relationship("RideModel", uselist=True, back_populates="driver")


class CarModel(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    model = Column(String)
    color = Column(String)
    plate_number = Column(String)
    year = Column(Integer)
    is_inclusive = Column(Boolean, default=False)
    
    driver = relationship("DriverModel", uselist=False, back_populates="car")


class LocationModel(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    ride_pick_up = relationship("RideModel", back_populates="pick_up_location_rel", uselist=False, foreign_keys="RideModel.pick_up_location")
    ride_destination = relationship("RideModel", back_populates="destination_rel", uselist=False, foreign_keys="RideModel.destination")


class RideStatusEnum(PythonEnum):
    SEARCHING = "searching"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"
    ORDERED = "ordered"


class RideModel(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    pick_up_location = Column(String, ForeignKey("locations.id"))
    destination = Column(String, ForeignKey("locations.id"))
    status = Column(Enum(RideStatusEnum), default=RideStatusEnum.SEARCHING)
    created_time = Column(DateTime, default=func.now())
    pick_up_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    client = relationship("ClientModel", back_populates="rides")
    driver = relationship("DriverModel", uselist=True, back_populates="rides")
    pick_up_location_rel = relationship("LocationModel", back_populates="ride_pick_up", foreign_keys=[pick_up_location])
    destination_rel = relationship("LocationModel", back_populates="ride_destination", foreign_keys=[destination])

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'driver_id': self.driver_id,
            'pick_up_location': self.pick_up_location,
            'destination': self.destination,
            'status': self.status,
            'created_time': self.created_time,
            'pick_up_time': self.pick_up_time,
            'start_time': self.start_time,
            'end_time': self.end_time,
        }


