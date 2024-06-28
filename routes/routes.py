from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import PredictionRequest, User
from utils import get_current_user
from services import predict_attendance_service, predict_attendance_chart_service, predict_result_service, login_for_access_token_service
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_for_access_token_service(form_data)

@router.post("/predict/")
async def predict_attendance(request: PredictionRequest, current_user: User = Depends(get_current_user)):
    return await predict_attendance_service(request, current_user)

@router.post("/predict/chart/")
async def predict_attendance_chart(request: PredictionRequest, current_user: User = Depends(get_current_user)):
    return await predict_attendance_chart_service(request, current_user)

@router.get("/predictResult/")
async def predict_result(current_user: User = Depends(get_current_user)):
    return await predict_result_service(current_user)