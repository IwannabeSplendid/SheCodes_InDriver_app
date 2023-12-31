import json
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

from .models import RideModel

class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


# Clients
class CreateClientRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: str

class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str


# Token
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'
    expires_in: int


# Ride
class CreateRideRequest(BaseModel):
    pick_up_location: str
    destination: str
    car_type: str
    notes: Optional[str]
    is_inclusive: Optional[bool]
    
    def to_dict(self):
        return {
            'pick_up_location': self.pick_up_location,
            'destination': self.destination,
            'car_type': self.car_type,
            'notes': self.notes,
            'is_inclusive': self.is_inclusive,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class CreateRideResponse(BaseModel):
    ride_id: int
    client_id: int
    driver_id: Optional[int]
    pick_up_location: str
    destination: str
    created_time: datetime
    notes: Optional[str]
    status: str
    
    def to_dict(self):
        return {
            'ride_id': self.ride_id,
            'client_id': self.client_id,
            'driver_id': self.driver_id,
            'car_type': 'car_type',
            'pick_up_location': self.pick_up_location,
            'destination': self.destination,
            'created_time': self.created_time.isoformat(),
            'notes': self.notes,
            'status': self.status,
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

class AssignDriverRequest(BaseModel):
    ride_id: int

class AssignDriverResponse(BaseModel):
    driver_first_name: str
    driver_last_name: str
    driver_license_number: str
    driver_contact_number: str
    driver_car: dict
    pick_up_location: str
    destination: str
    pick_up_time: datetime
    status: str
    
    def to_dict(self):
        return {
            'driver_first_name': self.driver_first_name,
            'driver_last_name': self.driver_last_name,
            'driver_license_number': self.driver_license_number,
            'driver_contact_number': self.driver_contact_number,
            'driver_car': self.driver_car,
            'pick_up_location': self.pick_up_location,
            'destination': self.destination,
            'pick_up_time': self.pick_up_time.isoformat(),
            'status': self.status,
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

class StartRideRequest(BaseModel):
    ride_id: int

class StartRideResponse(BaseModel):
    driver_first_name: str
    driver_last_name: str
    driver_license_number: str
    driver_contact_number: str
    driver_car: dict
    pick_up_location: str
    destination: str
    pick_up_time: datetime
    start_time: datetime
    end_time: datetime
    status: str
    
    def to_dict(self):
        return {
            'driver_first_name': self.driver_first_name,
            'driver_last_name': self.driver_last_name,
            'driver_license_number': self.driver_license_number,
            'driver_contact_number': self.driver_contact_number,
            'driver_car': self.driver_car,
            'pick_up_location': self.pick_up_location,
            'destination': self.destination,
            'pick_up_time': self.pick_up_time.isoformat(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

class StopRideRequest(BaseModel):
    ride_id: int
    rating: int

class ScheduleRideRequest(BaseModel):
    pick_up_location: str
    destination: str
    pick_dates_with_time: list[datetime]
    car_type: str
    notes: Optional[str]
    is_inclusive: bool

class VoiceBookRequest(BaseModel):
    voice_message: str

# Share ride
class ShareRideRequest(BaseModel):
    ride_id: int
    phone: str
