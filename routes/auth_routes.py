# auth_routes.py
from fastapi import APIRouter, HTTPException
from database import collection_user
from utils import verify_password,create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi import Depends
from fastapi.security import  OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = collection_user.find_one({"user_email": form_data.username})
    if user and verify_password(form_data.password, user['user_pw']):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"email": user['user_email']}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect email or password")

# @router.post("/users/")
# async def create_user(user: User):
#     # Check if the email is already registered
#     existing_user = collection_user.find_one({"email": user.user_email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Hash the password before storing in the database
#     hashed_password = hash_password(user.user_pw)
    
#     # Modify user data to include hashed password
#     user_data = user.dict()
#     user_data["user_pw"] = hashed_password

#     # Insert user data into MongoDB
#     inserted_user = collection_user.insert_one(user_data)

#     return {"message": "User created successfully", "user_id": str(inserted_user.inserted_id)}

# @router.post("/login")
# async def login(user_login: User_login):
#     # Retrieve user data for login using User_login model
#     existing_user = collection_user.find_one(
#         {"user_email": user_login.email}, 


        
#         {"_id": 0, "user_email": 1, "user_pw": 1, "user_type": 1}
#     )
#     if not existing_user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     user_pw = existing_user["user_pw"]  

#     if not verify_password(user_login.password, user_pw):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"email": user_login.email}, expires_delta=access_token_expires
#     )

#     return {"access_token": access_token, "type": existing_user.get("user_type")}
        