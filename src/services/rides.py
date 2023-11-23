import random
from sqlalchemy import and_
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta


from .security import get_current_client
from models import RideModel, DriverModel, ScheduleModel, LocationModel, RideStatusEnum


async def create_ride(data, db, current_user, scheduled=False, scheduled_pick_time=None):
    if scheduled:
        ride = db.query(RideModel).filter(RideModel.client_id == get_current_client(current_user).id).filter(RideModel.pick_up_time == scheduled_pick_time).first()
        if ride is not None:
            raise HTTPException(status_code=404, detail="Ride already scheduled.")
    
    _check_location([data.pick_up_location, data.destination])
    pick_up_location_id = _create_location(data.pick_up_location, db)
    destination_id = _create_location(data.destination, db)
    
    if scheduled:
        status = RideStatusEnum.ORDERED
    else:
        status = RideStatusEnum.SEARCHING
    
    new_ride = RideModel(
        client_id=get_current_client(current_user).id,
        driver_id=None,
        pick_up_location=pick_up_location_id,
        destination=destination_id,
        status=status,
    )

    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    return new_ride.to_dict()

async def assign_driver(data, db, scheduled=False, scheduled_ride_id=None, scheduled_pick_time=None):
    if scheduled:
        ride_id = scheduled_ride_id
    else:
        ride_id = data.ride_id

    ride = db.query(RideModel).filter(RideModel.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    
    if scheduled:
        schedules_at_the_time = db.query(ScheduleModel).filter(
            ScheduleModel.date == scheduled_pick_time.date(),
            and_(
                ScheduleModel.start_time <= scheduled_pick_time.time(),
                ScheduleModel.end_time >= scheduled_pick_time.time()
            )
            ).all()
        
        driver_ids_in_schedules = [schedule.driver_id for schedule in schedules_at_the_time]
        available_drivers = db.query(DriverModel).filter(~DriverModel.id.in_(driver_ids_in_schedules)).all()
        if len(available_drivers) == 0:
            raise HTTPException(status_code=404, detail="No available driver.")
        driver = random.choice(available_drivers)
    else:
        driver = db.query(DriverModel).filter(DriverModel.is_available_now == True).first()
        if driver is None:
            raise HTTPException(status_code=404, detail="No available driver.")
    
    ride.driver_id = driver.id
    if scheduled:
        ride.pick_up_time = scheduled_pick_time
    else:
        ride.pick_up_time = datetime.now() + timedelta(minutes=random.randint(1, 20))
        ride.status = RideStatusEnum.ACCEPTED
        driver.is_available_now = False
    
    ride.start_time = ride.pick_up_time + timedelta(minutes=random.randint(1, 5)) 
    ride.end_time = _create_schedule({'driver_id': driver.id, 'date': ride.start_time.date(), 'start_time': ride.start_time}, db)
    
    db.commit()
    db.refresh(ride)
    db.refresh(driver)
    
    pick_up_location = db.query(LocationModel).filter(LocationModel.id == ride.pick_up_location).first()
    destination = db.query(LocationModel).filter(LocationModel.id == ride.destination).first()
    
    ride_info = {
        "driver_first_name": driver.first_name,
        "driver_last_name": driver.last_name,
        "driver_license_number":  driver.license_number,
        "driver_contact_number" : driver.contact_number,
        "driver_car": {
            "model": driver.car.model,
            "color": driver.car.color,
            "plate_number": driver.car.plate_number,
            "year": driver.car.year,
            "is_inclusive": driver.car.is_inclusive,
        },
        "pick_up_location": pick_up_location.address,
        "destination": destination.address,
        "pick_up_time": ride.pick_up_time,
        "status": ride.status,
    }
    return ride_info

async def start_ride(data, db):
    ride = db.query(RideModel).filter(RideModel.id == data.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    
    driver = db.query(DriverModel).filter(DriverModel.id == ride.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver was not assigned.")
    
    ride.status = RideStatusEnum.STARTED
    
    pick_up_location = db.query(LocationModel).filter(LocationModel.id == ride.pick_up_location).first()
    destination = db.query(LocationModel).filter(LocationModel.id == ride.destination).first()
    
    ride_info = {
        "driver_first_name": driver.first_name,
        "driver_last_name": driver.last_name,
        "driver_license_number":  driver.license_number,
        "driver_contact_number" : driver.contact_number,
        "driver_car": {
            "model": driver.car.model,
            "color": driver.car.color,
            "plate_number": driver.car.plate_number,
            "year": driver.car.year,
            "is_inclusive": driver.car.is_inclusive,
        },
        "pick_up_location": pick_up_location.address,
        "destination": destination.address,
        "pick_up_time": ride.pick_up_time,
        'start_time': ride.start_time,
        'end_time': ride.end_time,
        "status": ride.status,
    }
    
    return ride_info

async def stop_ride(data, db):
    ride = db.query(RideModel).filter(RideModel.id == data.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    if ride.status != RideStatusEnum.STARTED:
        raise HTTPException(status_code=422, detail="Ride is not started.")
    
    ride.status = RideStatusEnum.COMPLETED
    
    driver = db.query(DriverModel).filter(DriverModel.id == ride.driver_id).first()
    driver.is_available_now = True
    
    db.query(ScheduleModel).filter(ScheduleModel.driver_id == driver.id).filter(ScheduleModel.date == ride.start_time.date()).filter(ScheduleModel.start_time==ride.start_time.time()).delete()
    
    db.commit()

async def schedule_ride(data, db, current_user):
    rides = []
    for pick_time in data.pick_dates_with_time:
        ride = await create_ride(data, db, current_user, scheduled=True, scheduled_pick_time=pick_time)
        ride_info = await assign_driver(data, db, scheduled=True, scheduled_ride_id=ride['id'], scheduled_pick_time=pick_time)
        rides.append(ride_info)
    
    return rides



# Helper functions
def _check_location(locations):
    for location in locations:
        if location.latitude > 90 or location.latitude < -90:
            raise HTTPException(status_code=422, detail="Invalid latitude.")
        if location.longitude > 180 or location.longitude < -180:
            raise HTTPException(status_code=422, detail="Invalid longitude.")

def _create_location(location, db):
    new_location = LocationModel(
        address=location.address,
        latitude=location.latitude,
        longitude=location.longitude
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location.id

def _get_ride_detail(ride_id, db):
    ride = db.query(RideModel).filter(RideModel.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    
    return ride

def _get_driver_detail(driver_id, db):
    driver = db.query(DriverModel).filter(DriverModel.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    
    return driver

def _create_schedule(data, db):
    driver = db.query(DriverModel).filter(DriverModel.id == data['driver_id']).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    
    end_datetime = data['start_time'] + timedelta(hours=1)
    schedule_entry = ScheduleModel(
        driver_id=driver.id,
        date=data['date'],
        start_time=data['start_time'].time(),
        end_time=end_datetime.time(),
    )

    db.add(schedule_entry)
    db.commit()

    return end_datetime