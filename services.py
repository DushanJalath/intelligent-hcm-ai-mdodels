import joblib
from datetime import datetime, timedelta
from functools import lru_cache
import asyncio
from fastapi import HTTPException
from utils import create_future_data
from models import PredictionRequest, User
from utils import create_access_token
import os
from fastapi.security import OAuth2PasswordRequestForm
from database import collection_user
from utils import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

@lru_cache()
def load_model():
    return joblib.load("rfmodel_leave.joblib")

rf_model = load_model()

async def login_for_access_token_service(form_data: OAuth2PasswordRequestForm):
    user = collection_user.find_one({"user_email": form_data.username})
    if user and verify_password(form_data.password, user['user_pw']):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"email": user['user_email']}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect email or password")

async def predict_attendance_service(request: PredictionRequest, current_user: User):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can predict attendance")
    try:
        future_data = await asyncio.to_thread(create_future_data, request.date)
        predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
        predicted_attendance_rounded = int(round(predicted_attendance[0]))  # Round to nearest integer
              
        return {"predicted_attendance": predicted_attendance_rounded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def predict_attendance_chart_service(request: PredictionRequest, current_user: User):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can approve vacancies")
    try:
        input_date = datetime.strptime(request.date, '%m%d')

        prediction_data = []
        for i in range(1, 8):
            next_date = (input_date + timedelta(days=i)).strftime('%m%d')
            future_data = await asyncio.to_thread(create_future_data, next_date)
            predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
            predicted_attendance_rounded = int(round(predicted_attendance[0]))  # Round to nearest integer
            prediction_data.append({"date": next_date, "predicted_attendance": predicted_attendance_rounded})

        return prediction_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def predict_result_service(current_user: User):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can predict attendance")
    try:
        future_data = await asyncio.to_thread(create_future_data, datetime.now().strftime('%m%d'))
        today_predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
        predicted_attendance_rounded = int(round(today_predicted_attendance[0]))  # Round to nearest integer
        
        Today_Total_Attendance = 180
        total_empolyee_count = 200
        Today_Total_Leave = total_empolyee_count - Today_Total_Attendance

        Today_Predicted_Leave = total_empolyee_count - predicted_attendance_rounded

        return {"Today_predicted_attendance": predicted_attendance_rounded, "Today_Total_Leave": Today_Total_Leave, "Today_Predicted_Leave": Today_Predicted_Leave, "total_empolyee_count": total_empolyee_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))