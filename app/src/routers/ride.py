import json
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from src.database import get_supabase_db
from models import (CreateRideRequest, CreateRideResponse, AssignDriverRequest,
                    AssignDriverResponse, StartRideRequest, StartRideResponse, ScheduleRideRequest,
                    ShareRideRequest, VoiceBookRequest, StopRideRequest)

from src.services import create_ride, assign_driver, start_ride, stop_ride, schedule_ride, share_ride_info
from src.services.chatGPT import translate_voice_message

from src.services.security import oauth2_scheme


ride_router = APIRouter(
    prefix="/rides",
    tags=["Rides"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)


@ride_router.post("/book_ride")
async def book_ride(request: CreateRideRequest, db = Depends(get_supabase_db), current_user: str = Depends(oauth2_scheme)):
    # headers = {"Authorization": f"Bearer {current_user}"}
    print(request)
    response = await create_ride(data=request, db=db, current_user=current_user)
    return response

@ride_router.post("/assign_driver")
async def assign_driver_to_ride(request: AssignDriverRequest, db = Depends(get_supabase_db)):
    response = await assign_driver(data=request, db=db)
    return AssignDriverResponse(**response)


@ride_router.post("/start_ride")
async def start_the_ride(request: StartRideRequest, db = Depends(get_supabase_db)):
    response = await start_ride(data=request, db=db)
    return response


@ride_router.post("/stop_ride")
async def stop_the_ride(request: StopRideRequest, db = Depends(get_supabase_db)):
    response = await stop_ride(data=request, db=db)
    return response


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
@ride_router.post("/voice_book_ride")
async def voice_book_ride(text_message: VoiceBookRequest, db = Depends(get_supabase_db), current_user: str = Depends(oauth2_scheme)):
    reply = await translate_voice_message(text_message)
    
    reply = json.loads(reply)

    if reply['scheduled'] == True:
        request = ScheduleRideRequest(
            pick_up_location=reply['pick_up_location'],
            destination=reply['destination'],
            pick_dates_with_time=reply['datetime'],
            car_type=reply['car_type'],
            notes=text_message.voice_message,
            is_inclusive=reply['is_inclusive']
        )

        response = await schedule_ride(data=request, db=db, current_user=current_user)
    else:
        request = CreateRideRequest(
            pick_up_location=reply["pick_up_location"],
            destination=reply["destination"],
            car_type=reply["car_type"],
            notes=text_message,
            is_inclusive=reply["is_inclusive"]
        )
        response = await create_ride(data=request, db=db, current_user=current_user)
    
    return response