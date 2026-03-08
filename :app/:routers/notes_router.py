from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from ..database import database
from ..models import books, notes
from ..schemas import NoteCreate, NoteOut
from .auth_router import get_current_user
router = APIRouter()

@router.post("/books/{book_id}/notes",response_model=NoteOut)
async def create_note(book_id:int,note:NoteCreate,current_user=Depends(get_current_user)):
    query = books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Book not borrowed hence note cant be added")
    details={
        "note": note.note ,"book_id":book_id,"created_at":datetime.utcnow()}
    insert_query=notes.insert().values(**details)
    note_id=await database.execute(insert_query)
    return NoteOut(id=note_id,**details)

@router.get("/books/{book_id}/notes",response_model=list[NoteOut])
async def get_notes(book_id:int,skip:int=0,limit:int=10, curent_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Book not borrowed hence note cant be fetched")
    fetch=(
        notes.select()
        .where(notes.c.book_id==book_id)
        .order_by(notes.c.created_at.desc())
        .offset(skip)
        .limit(limit))
    response = await database.fetch_all(fetch)
    return [NoteOut(**dict(row)) for row in response]

@router.put("/books/{book_id}/notes/{note_id",response_model=NoteOut)
async def update_note(book_id:int,note_id:int,new:NoteCreate, create_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Book not borrowed hence note cant be fetched")
    
    uquery=notes.select().where((notes.c.book_id==book_id) & (notes.c.id==note_id))
    data = await database.fetch_one(uquery)
    if not data:
        raise HTTPException(404,"Note not created hence note cant be fetched")

    update_query=(
        notes.update().where((notes.c.id==book_id)&(notes.c.id==note_id)).
        values(note=note.note, created_at=datetime.utcnow())
        )
    await database.execute(update_query)
    response=await database.fetch_one(query)
    return NoteOut(**dict(response))

@router.delete("/books/{book_id}/notes/{note_id")
async def delete_note(book_id:int,note_id:int,current_user=Depends(get_current_user)):
    query=books.select().where((books.c.user_id==current_user["id"]) & (books.c.id==book_id))
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(404,"Book not borrowed hence note cant be deleted")
    delete=notes.delete().where((notes.c.id==note_id)&(notes.c.book_id==book_id))
    response=await database.execute(delete)
    if response==0:
        raise HTTPException(404,"note not found")
    return {"message":"note deleted"}