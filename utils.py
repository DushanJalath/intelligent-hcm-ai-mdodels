import bcrypt
from jose import jwt
from jose.exceptions import JWTError
from fastapi import Depends
from datetime import datetime, timedelta
from fastapi import HTTPException
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import collection_user,collection_emp_time_rep,collection_leave_predictions_dataset
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    encoded_password = password.encode("utf-8")
    hashed = bcrypt.hashpw(encoded_password, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded_plain_password = plain_password.encode("utf-8")
    encoded_hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_plain_password, encoded_hashed_password)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def authenticate_user(email: str, password: str):
    existing_user = collection_user.find_one({"user_email": email})
    if not existing_user or not verify_password(password, existing_user["user_pw"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return existing_user


async def authenticate_user_exist(email: str):
    existing_user = collection_user.find_one({"user_email": email}, {"_id": 0, "user_email": 1, "user_type": 1})
    if not existing_user:
        raise HTTPException(status_code=401, detail="Incorrect email")
    return existing_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("Received Token:", token)
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = await authenticate_user_exist(email=payload)
    if user is None:
        raise credentials_exception
    return user


def is_holiday(date):
    future_holidays = {
        "0115": "Tamil Thai Pongal Day",
        "0125": "Duruthu Full Moon Poya Day",
        "0204": "Independence Day",
        "0223": "Navam Full Moon Poya Day",
        "0308": "Mahasivarathri Day",
        "0324": "Medin Full Moon Poya Day",
        "0329": "Good Friday",
        "0411": "Id-Ul-Fitr (Ramazan Festival Day)",
        "0412": "Day prior to Sinhala & Tamil New Year Day",
        "0413": "Sinhala & Tamil New Year Day",
        "0423": "Bak Full Moon Poya Day",
        "0501": "May Day (International Workers Day)",
        "0523": "Vesak Full Moon Poya Day",
        "0524": "Day following Vesak Full Moon Poya Day",
        "0617": "Id-Ul-Alha (Hadji Festival Day)",
        "0621": "Poson Full Moon Poya Day",
        "0720": "Esala Full Moon Poya Day",
        "0819": "Nikini Full Moon Poya Day",
        "0916": "Milad-Un-Nabi (Holy Prophet's Birthday)",
        "0917": "Binara Full Moon Poya Day",
        "1017": "Vap Full Moon Poya Day",
        "1031": "Deepavali Festival Day",
        "1115": "Ill Full Moon Poya Day",
        "1214": "Unduvap Full Moon Poya Day",
        "1225": "Christmas Day"
    }

    if date in future_holidays.keys():
        return 1
    else:
        return 0

def create_future_data(date):
    current_year = pd.Timestamp.now().year

    full_date_str = f"{current_year}-{date[:2]}-{date[2:]}"

    future_date_datetime = pd.to_datetime(full_date_str, format='%Y-%m-%d', errors='raise')
    print("Input Date:", future_date_datetime)

    next_day = future_date_datetime + pd.DateOffset(days=1)
    previous_day = future_date_datetime - pd.DateOffset(days=1)
    print("Next Day:", next_day)
    print("Previous Day:", previous_day)

    next_day_holiday = is_holiday(next_day.strftime("%m%d")) or next_day.dayofweek == 6
    previous_day_holiday = is_holiday(previous_day.strftime("%m%d")) or previous_day.dayofweek == 6
    print("Next Day Holiday:", next_day_holiday)
    print("Previous Day Holiday:", previous_day_holiday)

    is_holiday_flag = 1 if is_holiday(date) or future_date_datetime.dayofweek == 6 else 0
    print("Is Holiday Flag:", is_holiday_flag)

    day_of_week = future_date_datetime.dayofweek
    print("Day of the Week:", day_of_week)

    company_total_employee_count = 200

    if previous_day.dayofweek == 6 and next_day_holiday:
        previous_day_holiday = 1

    future_data = pd.DataFrame({
        "Previous day is a holiday": [previous_day_holiday],
        "Is Holiday": [is_holiday_flag],
        "Next day is a holiday": [next_day_holiday],
        "Day of the week": [day_of_week],
        "Company Total Employee Count": [200],
    })

    return future_data  

def update_leave_prediction_data():
    today = datetime.now().strftime('%Y-%m-%d')
    date_mmdd = datetime.now().strftime('%m%d')
    attendance = collection_emp_time_rep.find({"date": today, "totalWorkMilliSeconds": {"$gt": 0}})
    total_attendance = attendance.count()
    print("Total Attendance:", total_attendance)

    future_data = create_future_data(date_mmdd)

    leave_prediction_data = {
        "Date": int(date_mmdd),
        "Total Employee attendance Count": total_attendance,
        "Previous day is a holiday": future_data["Previous day is a holiday"].values[0],
        "Is Holiday": future_data["Is Holiday"].values[0],
        "Next day is a holiday": future_data["Next day is a holiday"].values[0],
        "Day of the week": future_data["Day of the week"].values[0],
        "Company Total Employee Count": future_data["Company Total Employee Count"].values[0]
    }
    collection_leave_predictions_dataset.insert_one(leave_prediction_data)
    logger.info(f"Updated leave prediction data for {today}.")


def schedule_daily_collection():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_leave_prediction_data, 'cron', hour=21, minute=0)
    scheduler.start()
    logger.info("Scheduled daily collection at 21:00.")
