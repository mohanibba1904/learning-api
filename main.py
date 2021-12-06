from fastapi import Depends, FastAPI
import logging
import jwt

from typing import Optional

from fastapi.security import OAuth2PasswordBearer 

import shelve
from pydantic import BaseModel
from pydantic.fields import Undefined

logging.basicConfig(filename="newfile.log",
format='%(asctime)s %(message)s',
         filemode='w')

class Profile(BaseModel):
    email: str
    date_of_birth: str 
    age: int

s = shelve.open("test", writeback = True)
s['auth'] = [] 


users_data = {'santosh': 123, "tarun": 234, 'manoj': 345}

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# encoded_jwt = jwt.encode({'some': "payload"}, "secret")

auth = Undefined

@app.get("/")
def read_root():
    return ({"Hello": "Wd"})

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/login")
def read_item(user_name:str, password:str):
    if user_name in users_data:
        user = users_data[user_name]
        if str(user) == password:
            payload_data = {"user_name": user_name}
            encoded_jwt = jwt.encode(payload=payload_data, key="secreat")
            s['auth'].append(encoded_jwt)
            return("login success", encoded_jwt)
        else:
            return("username and password not matched")

    else:
        return("login_error")

@app.post("/profile")
async def set_Item(profile: Profile):
    if s['auth'] == []:
        return("authentication required")
    else:
        return profile