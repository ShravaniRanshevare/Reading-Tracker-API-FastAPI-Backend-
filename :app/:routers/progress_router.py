from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from ..database import database
from ..models import books, reading_progress
from ..schemas import ProgressCreate, ProgressOut
from .auth_router import get_current_user
router = APIRouter()


@router.post("/books/{book_id}/progress",response_model=ProgressOut)
async def create_book_progress(book_id:int,progress:ProgressCreate,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data=await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Book not borrowed hence progress cant be added")
    insert_query=reading_progress.insert().values(book_id=book_id,pages_read=progress.pages_read,date=datetime.utcnow())
    response_id = await database.execute(insert_query)
    return ProgressOut(id=response_id,book_id=book_id,pages_read=progress.pages_read,date=datetime.utcnow())

@router.get("/books/{book_id}/progress",response_model=list[ProgressOut])
async def get_progress(book_id:int,skip: int = 0 , limit:int = 10, current_user=Depends(get_current_user)):
    query=(
        books.select()
        .where((books.c.user_id==current_user["id"]) & (books.c.id==book_id)))
    data=await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"user has not borrowed this book")
    get_query= (reading_progress.select()
               .where(reading_progress.c.book_id==book_id)
               .order_by(reading_progress.c.date.desc())
               .offset(skip)
               .limit(limit))
    result = await database.fetch_all(get_query)
    return [ProgressOut(**dict(row)) for row in result]

@router.put("/books/{book_id}/progress/{progress_id}",response_model=ProgressOut)
async def update_progress(book_id:int,progress_id:int ,new:ProgressCreate, current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data=await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"user has not borrowed this book")
    
    prog_query = (reading_progress.select()
                 .where((reading_progress.c.id == progress_id) & (reading_progress.c.book_id == book_id)))
    existing = await database.fetch_one(prog_query)
    if not existing:
        raise HTTPException(404, "Progress entry not found")
    
    update_query=(
        reading_progress.update().where((reading_progress.c.book_id==book_id)&(reading_progress.c.id==progress_id)).
        values(pages_read=new.pages_read, date=datetime.utcnow()))
    
    await database.execute(update_query)
    updated=await database.fetch_one(query)
    return ProgressOut(**dict(updated))

@router.delete("/books/{book_id}/progress/{progress_id}")
async def delete_progress(book_id:int,progress_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data=await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"user has not borrowed this book")
    
    query2=(reading_progress.delete().
    where((reading_progress.book_id==book_id) & (reading_progress.c.id==progress_id)))
    response=await database.execute(query2)
    if response==0:
        raise HTTPException(404,"given progress session has not been made")
    return {"message":"progress deleted"}