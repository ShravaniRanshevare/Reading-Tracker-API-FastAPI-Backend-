from sqlalchemy import Table,Column,Integer,String,ForeignKey,DateTime
from .database import metadata
from datetime import datetime

users=Table(
    "users",
    metadata,
    Column("id",Integer,primary_key=True),
    Column("username",String,unique=True,nullable=False),
    Column("email",String,unique=True,nullable=False),
    Column("password",String,nullable=False),)

books=Table(
    "books",
    metadata,
    Column("id",Integer,primary_key=True),
    Column("user_id",Integer,ForeignKey("users.id")),
    Column("title",String,nullable=False),
    Column("author",String,nullable=False),
    Column("genre",String),
    Column("total_pages",Integer),)

reading_progress=Table(
    "reading_progress",
     metadata,
     Column("id",Integer,primary_key=True),
     Column("book_id",Integer,ForeignKey("books.id")),
     Column("pages_read",Integer,nullable=False),
     Column("date",DateTime,default=datetime.utcnow),)

notes=Table(
    "notes",
    metadata,
    Column("id",Integer,primary_key=True),
    Column("book_id",Integer,ForeignKey("books.id")),
    Column("note",String,nullable=False),
    Column("created_at",DateTime,default=datetime.utcnow),)
    
    



