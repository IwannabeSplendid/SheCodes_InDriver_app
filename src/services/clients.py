
from datetime import datetime
from fastapi.exceptions import HTTPException


from models import ClientModel, RideModel, RideStatusEnum
from .security import get_password_hash


async def create_client_account(data, db):
    user = db.query(ClientModel).filter(ClientModel.email == data.email).first()
    if user:
        raise HTTPException(status_code=422, detail="Email is already registered with us.")

    new_user = ClientModel(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=get_password_hash(data.password),
        phone_number = data.phone_number,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_all_rides_history(data, db):
    client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
    rides = db.query(RideModel).filter(RideModel.client_id == client.id).all()
    return [ride.to_dict() for ride in rides]


async def get_completed_rides_history(data, db):
    client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
    print(RideStatusEnum.COMPLETED)
    rides = db.query(RideModel).filter(RideModel.client_id == client.id).filter(RideModel.status == RideStatusEnum.COMPLETED).all()
    return [ride.to_dict() for ride in rides]

async def get_ride_history(data, db, ride_id):
    client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
    ride = db.query(RideModel).filter(RideModel.client_id == client.id).filter(RideModel.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    return ride.to_dict()