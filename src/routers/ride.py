from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_db
from models import CreateRideRequest, CreateRideResponse, AssignDriverRequest, AssignDriverResponse, StartRideRequest, StartRideResponse, ScheduleRideRequest
from src.services import create_ride, assign_driver, start_ride, stop_ride, schedule_ride
from src.services.security import oauth2_scheme


ride_router = APIRouter(
    prefix="/rides",
    tags=["Rides"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)


@ride_router.post("/book_ride", response_model=CreateRideResponse)
async def book_ride(request: CreateRideRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
    # headers = {"Authorization": f"Bearer {current_user}"}
    response = await create_ride(data=request, db=db, current_user=current_user)
    return CreateRideResponse(
        ride_id=response['id'],
        client_id=response['client_id'],
        driver_id=response['driver_id'],
        pick_up_location=request.pick_up_location.address,
        destination=request.destination.address,
        created_time=response['created_time'],
        status=response['status'],
    )


@ride_router.post("/assign_driver", response_model=AssignDriverResponse)
async def assign_driver_to_ride(request: AssignDriverRequest, db: Session = Depends(get_db)):
    response = await assign_driver(data=request, db=db)
    return AssignDriverResponse(**response)


@ride_router.post("/start_ride", response_model=StartRideResponse)
async def start_the_ride(request: StartRideRequest, db: Session = Depends(get_db)):
    response = await start_ride(data=request, db=db)
    return StartRideResponse(**response)


@ride_router.post("/stop_ride")
async def stop_the_ride(request: StartRideRequest, db: Session = Depends(get_db)):
    await stop_ride(data=request, db=db)
    payload = {'message': 'Ride is successfully completed.'}
    return JSONResponse(content=payload)


@ride_router.post("/schedule_ride")
async def schedule_the_ride(request: ScheduleRideRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2_scheme)):
    response = await schedule_ride(data=request, db=db,current_user=current_user)
    return response

