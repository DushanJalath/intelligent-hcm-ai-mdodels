from pydantic import BaseModel

class User(BaseModel):
    user_id:str
    user_pw:str
    salary:float
    user_type:str
    address:str
    user_email:str
    project:str
    user_name:str
    contact:str
    manager_id:str 

class PredictionRequest(BaseModel):
    date: str

class PredictionResponse(BaseModel):
    date: str
    predicted_attendance: int
