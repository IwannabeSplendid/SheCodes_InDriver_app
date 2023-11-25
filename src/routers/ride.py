from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.database import get_supabase_db
from models import (CreateRideRequest, CreateRideResponse, AssignDriverRequest,
                    AssignDriverResponse, StartRideRequest, StartRideResponse, ScheduleRideRequest,
                    ShareRideRequest, VoiceBookRequest)

from src.services import create_ride, assign_driver, start_ride, stop_ride, schedule_ride, share_ride_info
from src.services.chatGPT import translate_voice_message

from src.services.security import oauth2_scheme


ride_router = APIRouter(
    prefix="/rides",
    tags=["Rides"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)


@ride_router.post("/book_ride", response_model=CreateRideResponse)
async def book_ride(request: CreateRideRequest, db = Depends(get_supabase_db), current_user: str = Depends(oauth2_scheme)):
    # headers = {"Authorization": f"Bearer {current_user}"}
    response = await create_ride(data=request, db=db, current_user=current_user)
    return CreateRideResponse(
        ride_id=response['id'],
        client_id=response['client_id'],
        driver_id=response['driver_id'],
        pick_up_location=request.pick_up_location,
        destination=request.destination,
        created_time=response['created_time'],
        status=response['status'],
    )

@ride_router.post("/assign_driver", response_model=AssignDriverResponse)
async def assign_driver_to_ride(request: AssignDriverRequest, db = Depends(get_supabase_db)):
    response = await assign_driver(data=request, db=db)
    return AssignDriverResponse(**response)


@ride_router.post("/start_ride", response_model=StartRideResponse)
async def start_the_ride(request: StartRideRequest, db = Depends(get_supabase_db)):
    response = await start_ride(data=request, db=db)
    return StartRideResponse(**response)


@ride_router.post("/stop_ride")
async def stop_the_ride(request: StartRideRequest, db = Depends(get_supabase_db)):
    await stop_ride(data=request, db=db)
    payload = {'message': 'Ride is successfully completed.'}
    return JSONResponse(content=payload)


@ride_router.post("/schedule_ride")
async def schedule_the_ride(request: ScheduleRideRequest, db = Depends(get_supabase_db), current_user: str = Depends(oauth2_scheme)):
    response = await schedule_ride(data=request, db=db,current_user=current_user)
    return response


# Share ride info
@ride_router.post("/share_ride")
async def share_ride(request: ShareRideRequest, current_user: str = Depends(oauth2_scheme)):
    response = await share_ride_info(data=request, current_user=current_user)
    return JSONResponse(response)


# Voice assistant
@ride_router.post("/voice_book_ride", response_model=CreateRideResponse)
async def voice_book_ride(voice_message: VoiceBookRequest, db = Depends(get_supabase_db), current_user: str = Depends(oauth2_scheme)):
    reply = await translate_voice_message(voice_message)
    
    if reply['scheduled'] == True:
        request = ScheduleRideRequest(
            pick_up_location=reply['pick_up_location'],
            destination=reply['destination'],
            pick_dates_with_time=reply['datetime'],
        )
        response = await schedule_ride(data=request, db=db, current_user=current_user)
    else:
        request = CreateRideRequest(
            pick_up_location=reply["pick_up_location"],
            destination=reply["destination"]
        )
        response = await create_ride(data=request, db=db, current_user=current_user)
    
    return CreateRideResponse(
        ride_id=response['id'],
        client_id=response['client_id'],
        driver_id=response['driver_id'],
        pick_up_location=reply['pick_up_location'],
        destination=reply['pick_up_location'],
        created_time=response['created_time'],
        status=response['status'],
    )
