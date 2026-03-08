from pydantic import BaseModel,EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str
    
class UserOut(BaseModel):
    id: int
    username:str
    email:EmailStr
    
    class Config:
        from_attributes=True
    
class BookCreate(BaseModel):
    title:str
    author:str
    genre:str | None
    total_pages:int | None
    
class BookOut(BookCreate):
    id:int
    user_id:int
    
    class Config:
        from_attributes=True
        
class ProgressCreate(BaseModel):
    pages_read:int

class ProgressOut(ProgressCreate):
    id:int
    book_id:int
    date:datetime
    
    class Config:
        from_attributes=True
        
        
class NoteCreate(BaseModel):
    note: str
    
class NoteOut(NoteCreate):
    id:int
    book_id:int
    created_at:datetime
    
    class Config:
        from_attributes=True
    
    
class BookAnalytics(BaseModel):
    book_id:int
    title:str
    total_pages:int|None
    pages_read:int
    progress_percent:float
    sessions:int
    last_read:datetime|None
    
class StreakOut(BaseModel):
    book_id:int
    current_streak:int
    longest_streak:int
    

class UserAnalytics(BaseModel):
    user_id:int
    total_books:int
    total_pages_read:int
    avg_speed:float
    top_genre:str|None
    active_days: list[str]
    keywords:list[str]
    
class Recommendation(BaseModel):
    reason: str
    suggestion: str
class ReadingSpeed(BaseModel):
    book_id:int
    pages_per_session:float
    pages_per_day:float
    
class FinishDate(BaseModel):
    book_id:int
    remaining_pages:int
    pages_per_day:float
    finish_date : datetime
    