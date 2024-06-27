from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import joblib
from datetime import datetime, timedelta
from database import collection_leave_predictions, collection_user
from models import PredictionRequest, User
from utils import create_future_data, get_current_user, is_holiday
from fastapi.responses import JSONResponse, StreamingResponse
import os
from functools import lru_cache
import asyncio
from datetime import datetime, timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@lru_cache()
def load_model():
    return joblib.load("rfmodel_leave.joblib") 

rf_model = load_model()

@router.post("/predict/")
async def predict_attendance(request: PredictionRequest, current_user: User = Depends(get_current_user)):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can predict attendance")
    try:
        future_data = await asyncio.to_thread(create_future_data, request.date)
        predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
        predicted_attendance_rounded = int(round(predicted_attendance[0]))  # Round to nearest integer
              
        return {"predicted_attendance": predicted_attendance_rounded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/chart/")
async def predict_attendance_chart(request: PredictionRequest, current_user: User = Depends(get_current_user)):
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

@router.get("/predictResult/")
async def predict_result(current_user: User = Depends(get_current_user)):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can predict attendance")
    try:
        future_data = await asyncio.to_thread(create_future_data, datetime.now().strftime('%m%d'))
        today_predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
        predicted_attendance_rounded = int(round(today_predicted_attendance[0]))  # Round to nearest integer
        
        Today_Total_Attendance = 180
        total_empolyee_count =200
        Today_Total_Leave = total_empolyee_count - Today_Total_Attendance

        Today_Predicted_Leave = total_empolyee_count - predicted_attendance_rounded

        return {"Today_predicted_attendance": predicted_attendance_rounded, "Today_Total_Leave": Today_Total_Leave ,  "Today_Predicted_Leave": Today_Predicted_Leave ,"total_empolyee_count": total_empolyee_count }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
