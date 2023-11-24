from celery import Celery
from sqlalchemy import and_
from datetime import datetime, timedelta


from .database import get_db
from models import RideModel, DriverModel, RideStatusEnum, ScheduleModel


app = Celery('tasks', broker='pyamqp://guest:guest@localhost//')


@app.task(ignore_result=True, name='tasks.schedule_check')
def check_and_update_schedules():
    db = next(get_db())
    ended_rides = db.query(RideModel).filter(RideModel.end_time <= datetime.now()).all()

    for ride in ended_rides:
        ride.status = RideStatusEnum.CANCELLED
        schedule = db.query(ScheduleModel).filter(ScheduleModel.ride_id == ride.id).delete()

    db.commit()
    db.close()

@app.task(ignore_result=True, name='tasks.driver_status_update')
def check_and_update_driver_status():
    db = next(get_db())
    drivers = db.query(DriverModel).all()

    for driver in drivers:
        schedules = db.query(ScheduleModel).filter(ScheduleModel.driver_id == driver.id).filter(ScheduleModel.date == datetime.now().date(),
                                                    and_(
                                                        ScheduleModel.start_time <= (datetime.now() - timedelta(minutes=30)).time(),
                                                        ScheduleModel.start_time >= datetime.now().time()
                                                    )).all()
        if len(schedules) == 0:
            driver.is_available_now = True
        else:
            driver.is_available_now = False

    db.commit()
    db.close()

@app.task(ignore_result=True, name='tasks.periodic_start')
@app.on_after_configure.connect
def periodic_task(sender, **kwargs):
    sender.add_periodic_task(120, check_and_update_driver_status(), name='update driver status')
    sender.add_periodic_task(120, check_and_update_schedules(), name='update schedules')
