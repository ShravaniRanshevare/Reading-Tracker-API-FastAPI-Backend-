
from datetime import timedelta,datetime
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


SECRET_KEY = os.getenv("SECRET_KEY","dev_secret_key")
ALGORITHM= os.getenv("ALGORITHM","HS256") # replace in_TOKEN_EXPIRE_MIN = "HS256" ACCESSUTES = 60
expiry=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


def hash_password(password:str) -> str:
    return pwd_context.hash(password)

def verify_password(plain:str,hashed:str):
    return pwd_context.verify(plain,hashed)

def create_access_token(data:dict):
    to_encode=data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expiry)
    to_encode.update({"exp":expire})
    token_id=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token_id

def decode_access_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
    

    

    