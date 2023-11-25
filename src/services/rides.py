import random
import json
from sqlalchemy import and_
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta


from .security import get_current_client
from models import RideModel, DriverModel, ScheduleModel, RideStatusEnum

# Local DB
# async def create_ride_local_db(data, db, current_user, scheduled=False, scheduled_pick_time=None):
#     if scheduled:
#         ride = db.query(RideModel).filter(RideModel.client_id == get_current_client(current_user).id).filter(RideModel.pick_up_time == scheduled_pick_time).first()
#         if ride is not None:
#             raise HTTPException(status_code=404, detail="Ride already scheduled.")
    
#     if scheduled:
#         status = RideStatusEnum.ORDERED
#     else:
#         status = RideStatusEnum.SEARCHING
    
#     new_ride = RideModel(
#         client_id=get_current_client(current_user).id,
#         driver_id=None,
#         pick_up_location=data.pick_up_location,
#         destination=data.destination,
#         status=status,
#     )

#     db.add(new_ride)
#     db.commit()
#     db.refresh(new_ride)
#     return new_ride.to_dict()

# async def assign_driver(data, db, scheduled=False, scheduled_ride_id=None, scheduled_pick_time=None):
#     if scheduled:
#         ride_id = scheduled_ride_id
#     else:
#         ride_id = data.ride_id

#     ride = db.query(RideModel).filter(RideModel.id == ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found.")
    
#     if scheduled:
#         schedules_at_the_time = db.query(ScheduleModel).filter(
#             ScheduleModel.date == scheduled_pick_time.date(),
#             and_(
#                 ScheduleModel.start_time <= scheduled_pick_time.time(),
#                 ScheduleModel.end_time >= scheduled_pick_time.time()
#             )
#             ).all()
        
#         driver_ids_in_schedules = [schedule.driver_id for schedule in schedules_at_the_time]
#         available_drivers = db.query(DriverModel).filter(~DriverModel.id.in_(driver_ids_in_schedules)).all()
#         if len(available_drivers) == 0:
#             raise HTTPException(status_code=404, detail="No available driver.")
#         driver = random.choice(available_drivers)
#     else:
#         driver = db.query(DriverModel).filter(DriverModel.is_available_now == True).first()
#         if driver is None:
#             raise HTTPException(status_code=404, detail="No available driver.")
    
#     ride.driver_id = driver.id
#     if scheduled:
#         ride.pick_up_time = scheduled_pick_time
#     else:
#         ride.pick_up_time = datetime.now() + timedelta(minutes=random.randint(1, 20))
#         ride.status = RideStatusEnum.ACCEPTED
#         driver.is_available_now = False
    
#     ride.start_time = ride.pick_up_time + timedelta(minutes=random.randint(1, 5)) 
#     ride.end_time = _create_schedule({'driver_id': driver.id, 'date': ride.start_time.date(), 'start_time': ride.start_time, 'ride_id': ride.id}, db)
    
#     db.commit()
#     db.refresh(ride)
#     db.refresh(driver)
    
#     pick_up_location = db.query(LocationModel).filter(LocationModel.id == ride.pick_up_location).first()
#     destination = db.query(LocationModel).filter(LocationModel.id == ride.destination).first()
    
#     ride_info = {
#         "driver_first_name": driver.first_name,
#         "driver_last_name": driver.last_name,
#         "driver_license_number":  driver.license_number,
#         "driver_contact_number" : driver.contact_number,
#         "driver_car": {
#             "model": driver.car.model,
#             "color": driver.car.color,
#             "plate_number": driver.car.plate_number,
#             "year": driver.car.year,
#             "is_inclusive": driver.car.is_inclusive,
#         },
#         "pick_up_location": pick_up_location.address,
#         "destination": destination.address,
#         "pick_up_time": ride.pick_up_time,
#         "status": ride.status,
#     }
#     return ride_info

# async def start_ride(data, db):
#     ride = db.query(RideModel).filter(RideModel.id == data.ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found.")
    
#     driver = db.query(DriverModel).filter(DriverModel.id == ride.driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver was not assigned.")
    
#     ride.status = RideStatusEnum.STARTED
    
#     pick_up_location = db.query(LocationModel).filter(LocationModel.id == ride.pick_up_location).first()
#     destination = db.query(LocationModel).filter(LocationModel.id == ride.destination).first()
    
#     ride_info = {
#         "driver_first_name": driver.first_name,
#         "driver_last_name": driver.last_name,
#         "driver_license_number":  driver.license_number,
#         "driver_contact_number" : driver.contact_number,
#         "driver_car": {
#             "model": driver.car.model,
#             "color": driver.car.color,
#             "plate_number": driver.car.plate_number,
#             "year": driver.car.year,
#             "is_inclusive": driver.car.is_inclusive,
#         },
#         "pick_up_location": pick_up_location.address,
#         "destination": destination.address,
#         "pick_up_time": ride.pick_up_time,
#         'start_time': ride.start_time,
#         'end_time': ride.end_time,
#         "status": ride.status,
#     }
    
#     return ride_info

# async def stop_ride(data, db):
#     ride = db.query(RideModel).filter(RideModel.id == data.ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found.")

#     if ride.status != RideStatusEnum.STARTED:
#         raise HTTPException(status_code=422, detail="Ride is not started.")
    
#     ride.status = RideStatusEnum.COMPLETED
    
#     driver = db.query(DriverModel).filter(DriverModel.id == ride.driver_id).first()
#     driver.is_available_now = True
    
#     db.query(ScheduleModel).filter(ScheduleModel.driver_id == driver.id).filter(ScheduleModel.date == ride.start_time.date()).filter(ScheduleModel.start_time==ride.start_time.time()).delete()
    
#     db.commit()

# async def schedule_ride(data, db, current_user):
#     rides = []
#     for pick_time in data.pick_dates_with_time:
#         ride = await create_ride(data, db, current_user, scheduled=True, scheduled_pick_time=pick_time)
#         ride_info = await assign_driver(data, db, scheduled=True, scheduled_ride_id=ride['id'], scheduled_pick_time=pick_time)
#         rides.append(ride_info)
    
#     return rides


# Supabase DB
async def create_ride(data, db, current_user):
    client_id = get_current_client(current_user)['id']
    new_ride = {
        'client_id': client_id,
        'driver_id': None,
        'pick_up_location': data.pick_up_location,
        'destination': data.destination,
        'car_type': data.car_type,
        'notes': data.notes,
        'is_inclusive': data.is_inclusive,
        'status': "searching",
    }

    ride = db.table('rides').insert(new_ride).execute().data[0]

    return ride

async def assign_driver(data, db, scheduled=False, scheduled_ride_id = None, scheduled_pick_time=None, driver=None):
    if scheduled:
        ride_id = scheduled_ride_id
    else:
        ride_id = data.ride_id
    
    ride = db.table('rides').select('*').eq('id', ride_id).limit(1).execute().data
    if len(ride) == 0:
        raise HTTPException(status_code=404, detail="Ride not found.")
    
    ride = ride[0]
    if ride['status'] != "searching":
        raise HTTPException(status_code=422, detail="Ride is already assigned to a driver.")
    
    if scheduled:
        driver = driver
    else:        
        if ride['is_inclusive']:
            cars = db.table('cars').select('id').eq('car_type', ride['car_type']).eq('is_inclusive', True).execute().data
        else:
            cars = db.table('cars').select('id').eq('car_type', ride['car_type']).execute().data
        
        cars_id = [car['id'] for car in cars]
        
        driver = db.table('drivers').select('*').eq('is_available_now', True).in_('car_id', cars_id).limit(1).execute().data
        
        if len(driver) == 0:
            raise HTTPException(status_code=404, detail="No available driver.")
        
        driver = driver[0]

    if scheduled:
        pick_up_time = scheduled_pick_time
    else:
        pick_up_time = datetime.now() + timedelta(minutes=random.randint(1, 20))
        driver = db.table('drivers').update({"is_available_now": False}).eq('id', driver['id']).execute().data[0]

    status = "ordered" if scheduled else "accepted"
    start_time = pick_up_time + timedelta(minutes=random.randint(1, 5)) 
    end_time = _create_schedule({'driver_id': driver['id'], 'date': start_time.date(), 'start_time': start_time, 'ride_id': ride['id']}, db)
    ride = db.table('rides').update({"pick_up_time": pick_up_time.isoformat() , "status": status, "driver_id": driver['id'], "start_time": start_time.isoformat(), "end_time": end_time.isoformat()}).eq('id', ride['id']).execute().data[0]
    car = db.table('cars').select('*').eq('driver_id', driver['id']).limit(1).execute().data[0]
    
    ride_info = {
        "driver_first_name": driver['first_name'],
        "driver_last_name": driver['last_name'],
        "driver_license_number":  driver['license_number'],
        "driver_contact_number" : driver['contact_number'],
        "driver_car": {
            "model": car['model'],
            "color": car['color'],
            "plate_number": car['plate_number'],
            "year": car['year'],
            "is_inclusive": car['is_inclusive'],
            "car_type": car['car_type'],
        },
        "pick_up_location": ride['pick_up_location'],
        "destination": ride['destination'],
        "pick_up_time": ride['pick_up_time'],
        "notes": ride['notes'],
        "status": ride['status'],
    }
    return ride_info

async def start_ride(data, db):
    ride = db.table('rides').select('*').eq('id', data.ride_id).limit(1).execute().data
    if len(ride) == 0:
        raise HTTPException(status_code=404, detail="Ride not found.")
    ride = ride[0]
    
    driver = db.table('drivers').select('*').eq('id', ride['driver_id']).limit(1).execute().data
    if len(driver) == 0:
        raise HTTPException(status_code=404, detail="Driver was not assigned.")
    driver = driver[0]
    
    ride = db.table('rides').update({"status": "started"}).eq('id', ride['id']).execute().data[0]
    car = db.table('cars').select('*').eq('driver_id', driver['id']).limit(1).execute().data[0]
    
    ride_info = {
        "driver_first_name": driver['first_name'],
        "driver_last_name": driver['last_name'],
        "driver_license_number":  driver['license_number'],
        "driver_contact_number" : driver['contact_number'],
        "driver_car": {
            "model": car['model'],
            "color": car['color'],
            "plate_number": car['plate_number'],
            "year": car['year'],
            "is_inclusive": car['is_inclusive'],
            "car_type": car['car_type'],
        },
        "pick_up_location": ride['pick_up_location'],
        "destination": ride['destination'],
        "pick_up_time": ride['pick_up_time'],
        'start_time': ride['start_time'],
        'end_time': ride['end_time'],
        "notes": ride['notes'],
        "status": ride['status'],
    }
    return ride_info

async def stop_ride(data, db):
    ride = db.table('rides').select('*').eq('id', data.ride_id).limit(1).execute().data
    if len(ride) == 0:
        raise HTTPException(status_code=404, detail="Ride not found.")
    ride = ride[0]
    
    if ride['status'] != "started":
        raise HTTPException(status_code=422, detail="Ride is not started.")
    
    db.table('rides').update({"status": "completed"}).eq('id', ride['id']).execute()
    driver = db.table('drivers').update({"is_available_now": True}).eq('id', ride['driver_id']).execute().data[0]
    d_rating = driver['rating']
    d_rating_count = float(driver['n_ratings'])
    d_rating = (d_rating * d_rating_count + data.rating) / (d_rating_count + 1)
    db.table('drivers').update({"rating": d_rating, "n_ratings": int(d_rating_count + 1)}).eq('id', ride['driver_id']).execute()
    db.table('schedules').delete().eq('ride_id', ride['id']).execute()
    
    car = db.table('cars').select('*').eq('driver_id', driver['id']).limit(1).execute().data[0]
    
    ride_info = {
        "driver_first_name": driver['first_name'],
        "driver_last_name": driver['last_name'],
        "driver_license_number":  driver['license_number'],
        "driver_contact_number" : driver['contact_number'],
        "driver_rating": driver['rating'],
        "driver_n_rating": driver['n_ratings'],
        "driver_car": {
            "model": car['model'],
            "color": car['color'],
            "plate_number": car['plate_number'],
            "year": car['year'],
            "is_inclusive": car['is_inclusive'],
            "car_type": car['car_type'],
        },
        "pick_up_location": ride['pick_up_location'],
        "destination": ride['destination'],
        "pick_up_time": ride['pick_up_time'],
        'start_time': ride['start_time'],
        'end_time': ride['end_time'],
        'notes': ride['notes'],
        "status": ride['status'],
    }
    return ride_info

async def schedule_ride(data, db, current_user):
    client_id = get_current_client(current_user)['id']
    drivers = []
    for pick_time in data.pick_dates_with_time:
        scheduled_pick_time_u1 = pick_time + timedelta(minutes=1)
        scheduled_pick_time_d1 = pick_time - timedelta(minutes=1)
        ride = db.table('rides').select('*').eq('client_id', client_id).lte('pick_up_time', scheduled_pick_time_u1.isoformat()).gte('pick_up_time', scheduled_pick_time_d1.isoformat()).limit(1).execute().data

        if len(ride) != 0:
            raise HTTPException(status_code=404, detail="One of the rides is already scheduled.")
        
        schedules_at_the_time = db.table('schedules').select('*').eq('date', pick_time.date()).gte('start_time', pick_time.time()).lte('end_time', pick_time.time()).execute().data

        driver_ids_in_schedules = [schedule['driver_id'] for schedule in schedules_at_the_time]
        available_drivers = db.table('drivers').select('*').not_.in_('id', driver_ids_in_schedules).execute().data

        
        if len(available_drivers) == 0:
            raise HTTPException(status_code=404, detail="No available driver.")

        driver = random.choice(available_drivers)
        drivers.append(driver)

    rides = []
    for i, pick_time in enumerate(data.pick_dates_with_time):
        ride = await create_ride(data, db, current_user)
        ride_info = await assign_driver(data, db, scheduled=True, scheduled_ride_id = ride['id'], scheduled_pick_time=pick_time, driver=drivers[i])
        rides.append(ride_info)
    
    return rides



# Helper functions
def _create_schedule(data, db):
    driver = db.table('drivers').select('*').eq('id', data['driver_id']).limit(1).execute().data
    if len(driver) == 0:
        raise HTTPException(status_code=404, detail="Driver not found.")
    driver = driver[0]
    
    end_datetime = data['start_time'] + timedelta(hours=1)
    schedule_entry = {
        'driver_id': driver['id'],
        'date': data['date'].isoformat(),
        'ride_id': data['ride_id'],
        'start_time': data['start_time'].time().isoformat(),
        'end_time': end_datetime.time().isoformat(),
    }
    
    db.table('schedules').insert(schedule_entry).execute()

    return end_datetime
