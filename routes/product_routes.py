from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, UploadFile
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

router = APIRouter()

# Define your OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load the machine learning model once at startup
@lru_cache()
def load_model():
    # rfmodel_leave
    return joblib.load("rfmodel_leave.joblib") 

rf_model = load_model()

@router.post("/predict/")
async def predict_attendance(request: PredictionRequest, current_user: User = Depends(get_current_user)):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can predict attendance")
    try:
        # Predict attendance for the given date
        future_data = await asyncio.to_thread(create_future_data, request.date)
        predicted_attendance = await asyncio.to_thread(rf_model.predict, future_data)
        predicted_attendance_rounded = int(round(predicted_attendance[0]))  # Round to nearest integer
        
        # Store prediction in MongoDB
        # await collection_leave_predictions.insert_one({"date": request.date, "predicted_attendance": predicted_attendance_rounded})

        return {"predicted_attendance": predicted_attendance_rounded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/chart/")
async def predict_attendance_chart(request: PredictionRequest, current_user: User = Depends(get_current_user)):
    if current_user.get('user_type') not in ["HR", "Manager"]:
        raise HTTPException(status_code=403, detail="Unauthorized, only HR can approve vacancies")
    try:
        # Convert the input date to a datetime object
        input_date = datetime.strptime(request.date, '%m%d')

        # Create data for the next 7 days
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
