from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from ..database import database
from ..models import users
from ..schemas import UserCreate, UserOut
from ..auth import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register",response_model=UserOut)
async def register(user : UserCreate):
    query = users.select().where((users.c.username==user.username) | (users.c.email==user.email))
    response = await database.fetch_all(query)
    if response:
        raise HTTPException(400,"username exists")
    else:
        password = hash_password(user.password)
        query = users.insert().values(username=user.username,email=user.email,password=password)
        user_id = await database.execute(query)
        return UserOut(id=user_id,username=user.username,email=user.email)
    
    

@router.post("/login")
async def login(form_data:OAuth2PasswordRequestForm=Depends()):
    query = users.select().where(users.c.username == form_data.username)
    user = await database.fetch_one(query)
    
    if not user or not verify_password(form_data.password,user["password"]):
        raise HTTPException(401,"Inavlid username or password")
    
    token=create_access_token({"sub":user["username"]})
    return {"access_token":token,"token_type":"bearer"}

@router.post("/me")
async def get_current_user(token:str = Depends(oauth2_scheme)):
    username = decode_access_token(token)
    if not username:
        raise HTTPException(401,"Invalid or expired token")
    query = users.select().where(users.c.username==username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(401,"user no longer exists")
    return user