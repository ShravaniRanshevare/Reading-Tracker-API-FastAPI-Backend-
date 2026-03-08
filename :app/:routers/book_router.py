from fastapi import APIRouter, Depends, HTTPException
from ..database import database
from ..models import books
from ..schemas import BookCreate, BookOut
from .auth_router import get_current_user
from ..services.cache_service import get_cache,set_cache
router = APIRouter()

@router.post("/books",response_model=BookOut)
async def create_book(book:BookCreate,current_user=Depends(get_current_user)):
    data=book.dict()
    data["user_id"]=current_user["id"]
    query=books.insert().values(**data)
    book_id=await database.execute(query)
    
    return BookOut(id=book_id,user_id=current_user["id"],**book.dict())

@router.put("/books/{book_id}",response_model=BookOut)
async def update_book(book_id:int,new_book:BookCreate,current_user=Depends(get_current_user)):
    query = books.select().where((books.c.id==book_id)&(books.c.user_id==current_user["id"]))
    book=await database.fetch_one(query)
    if not book:
        raise HTTPException(404,"Book not found")
    update_query=(books.update().where(books.c.id==book_id).values(**new_book.dict()))
    await database.execute(update_query)
    
    updated=database.fetch_one(query)
    return BookOut(**dict(updated))
    

@router.get("/books",response_model=list[BookOut])
async def get_books(skip:int=0,limit:int= 10, current_user=Depends(get_current_user)):
    cache_key=f"books:{current_user['id']}"
    cached= await get_cache(cache_key)
    if cached:
        return cached
    
    query=(
        books.select()
        .where(books.c.user_id==current_user["id"])
        .offset(skip).limit(limit))
        
    data = await database.fetch_all(query)
    if not data:
        raise HTTPException(404,"Books not found for this user")
    result =  [BookOut(**dict(row)) for row in data]
    await set_cache(cache_key,[r.dict() for r in result],ttl=60)
    return result

    
@router.get("/books/{book_id}",response_model=BookOut)
async def get_book(book_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Books not found for this user")
    return BookOut(id=book_id,user_id=current_user["id"],**dict(data))

@router.delete("/books/{book_id}")
async def delete_book(book_id:int,current_user=Depends(get_current_user)):
    query=books.delete().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    response = await database.execute(query)
    if response==0 :
        raise HTTPException(404,"Book not found for this user")
    return {"message":"book deleted"}

