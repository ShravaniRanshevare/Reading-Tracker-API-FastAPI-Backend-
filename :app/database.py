from sqlalchemy import create_engine,MetaData
from databases import Database
from dotenv import load_dotenv,dotenv_values
import os

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

DATABASE_URL= os.getenv("DATABASE_URL","sqlite:///./reading.db")
database=Database(DATABASE_URL)
metadata=MetaData()
engine = create_engine(DATABASE_URL) # IMPORTANT: create tables
def create_tables():
    metadata.create_all(engine)
    
    


