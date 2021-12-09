from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

from library import crud,models, schemas
from datetime import datetime, timedelta 
from library.database import SessionLocal, engine
from typing import Optional
# from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://127.0.0.1:8000/login",
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    

pwd_context= CryptContext(schemes=["bcrypt"],deprecated='auto')



@app.get("/users_details/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users_details/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user





# @app.get("/login")
# def read_item(user_name:str, password:str,db: Session = Depends(get_db)):
#     users = crud.get_users(db)
#     us = ''
#     ps= ''
#     for i in users:
#         if(i.user_name == user_name):
#             us = i.user_name
#             ps = i.password
#     if user_name == us:
#         if str(ps) == password:
#             payload_data = {"user_name": user_name}
#             encoded_jwt = jwt.encode(payload=payload_data, key="secreat")
#             s['auth'].append(encoded_jwt)
#             return("login success", encoded_jwt)
#         else:
#             return("username and password not matched")

#     else:
#         return("login error")

@app.post('/signup')
def create_user(request:schemas.User,db: Session = Depends(get_db)):
    hashedPassword=pwd_context.hash(request.password)
    new_user=models.User(user_name=request.user_name, email=request.email,password=hashedPassword)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post('/login')
def login(request:schemas.Data,db:Session= Depends(get_db)):
    
    current_user=db.query(models.User).filter(models.User.user_name == request.user_name).first()
    hashedPassword = current_user.password
    
    is_valid=pwd_context.verify(request.password, hashedPassword)
    if is_valid:
        access_token = create_access_token(data={"sub": current_user.user_name})
        return{"access_token":access_token, "token_type":"bearer"}
        
    return "user not found"
    