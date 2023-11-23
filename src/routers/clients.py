from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from models import CreateClientRequest, ClientResponse, RideModel
from src.services import create_client_account, get_all_rides_history, get_completed_rides_history, get_ride_history
from src.services.security import oauth2_scheme, get_current_client


user_router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    responses={404: {"description": "Not found"}},
)


client_router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)


@user_router.post('', status_code=status.HTTP_201_CREATED)
async def create_client(data: CreateClientRequest, db: Session = Depends(get_db)):
    await create_client_account(data=data, db=db)
    payload = {"message": "Client account has been succesfully created."}
    return JSONResponse(content=payload)


@client_router.get('/profile', status_code=status.HTTP_200_OK, response_model=ClientResponse)
def get_client_detail(request: Request):
    return request.user


@client_router.get('/rides', status_code=status.HTTP_200_OK)
async def get_rides_history(request: Request, db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
    client = get_current_client(current_user)
    response = await get_all_rides_history(data=client, db=db)
    return response


@client_router.get('/rides/completed', status_code=status.HTTP_200_OK)
async def get_completed_rides(request: Request, db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
    client = get_current_client(current_user)
    response = await get_completed_rides_history(data=client, db=db)
    return response


@client_router.get('/rides/{ride_id}', status_code=status.HTTP_200_OK)
async def get_the_ride_history(request: Request, ride_id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
    client = get_current_client(current_user)
    response = await get_ride_history(data=client, db=db, ride_id=ride_id)  
    return response


