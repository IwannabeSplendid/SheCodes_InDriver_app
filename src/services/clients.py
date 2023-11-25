
from fastapi.exceptions import HTTPException


from models import ClientModel, RideModel, RideStatusEnum
from .security import get_password_hash


async def create_client_account(data, db, local = False):
    if local:
        user = db.query(ClientModel).filter(ClientModel.email == data.email).first()
    else:
        user = db.table('clients').select('*').eq('email', data.email).limit(1).execute().data

    if len(user) != 0:
        raise HTTPException(status_code=422, detail="Email is already registered with us.")

    if local:
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
    else:
        new_user = {
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "password": get_password_hash(data.password),
            "phone_number": data.phone_number,
        }
        
        db.table('clients').insert(new_user).execute()
    
    return new_user


async def get_all_rides_history(data, db, local = False):
    if local:
        client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
        rides = db.query(RideModel).filter(RideModel.client_id == client.id).all()
    else:
        client = db.table('clients').select('*').eq('id', data['id']).limit(1).execute().data
        
        if len(client) == 0:
            raise HTTPException(status_code=404, detail="Client not found.")
        
        rides = db.table('rides').select('*').eq('client_id', client[0]['id']).execute().data

    return rides


async def get_completed_rides_history(data, db, local = False):
    if local:
        client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
        rides = db.query(RideModel).filter(RideModel.client_id == client.id).filter(RideModel.status == RideStatusEnum.COMPLETED).all()
    else:
        client = db.table('clients').select('*').eq('id', data['id']).limit(1).execute().data
        
        if len(client) == 0:
            raise HTTPException(status_code=404, detail="Client not found.")
        
        rides = db.table('rides').select('*').eq('client_id', client[0]['id']).eq('status', "completed").execute().data
    
    return rides

async def get_ride_history(data, db, ride_id, local = False):
    if local:
        client = db.query(ClientModel).filter(ClientModel.id == data.id).first()
        ride = db.query(RideModel).filter(RideModel.client_id == client.id).filter(RideModel.id == ride_id).first()
    else:
        client = db.table('clients').select('*').eq('id', data['id']).limit(1).execute().data
        
        if len(client) == 0:
            raise HTTPException(status_code=404, detail="Client not found.")
        
        ride = db.table('rides').select('*').eq('client_id', client[0]['id']).eq('id', ride_id).limit(1).execute().data
    
        if len(ride) == 0:
            raise HTTPException(status_code=404, detail="Ride not found.")

    return ride[0]