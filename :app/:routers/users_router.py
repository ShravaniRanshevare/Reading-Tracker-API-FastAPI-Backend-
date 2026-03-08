from fastapi import APIRouter, Depends, HTTPException
from ..database import database
from ..models import users
from ..schemas import UserCreate, UserOut
from .auth_router import get_current_user
from ..auth import hash_password


router = APIRouter()


@router.get("/users",response_model=list[UserOut])
async def get_users(skip=50,limit=50):
    query=users.select().offset(skip).limit(limit)
    data = await database.fetch_all(query)
    return [UserOut(**dict(row)) for row in data]

@router.post("/users",response_model=UserOut)
async def create_user(user: UserCreate):
    # check duplicates
    query = users.select().where(
        (users.c.username == user.username) | (users.c.email == user.email)
    )
    existing = await database.fetch_one(query)   # ✔ do NOT overwrite user

    if existing:
        raise HTTPException(400, "Username or email already exists")

    # hash password correctly
    hashed = hash_password(user.password)

    # insert
    insert_query = users.insert().values(
        username=user.username,
        email=user.email,
        password=hashed
    )
    user_id = await database.execute(insert_query)

    return UserOut(id=user_id, username=user.username, email=user.email)


@router.get("/users/{user_id}")
async def get_user(user_id:int):
    query=users.select().where(users.c.id==user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(404,"User not found")
    return user
    
@router.delete("/users/{user_id}")
async def delete_user(user_id:int):
    query=users.delete().where(users.c.id==user_id)
    result = await database.execute(query)
    if result == 0:
        raise HTTPException(404,"User not found")
    return {"message":"user deleted"}