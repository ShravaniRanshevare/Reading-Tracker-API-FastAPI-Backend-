from app.models import metadata
from app.database import engine

metadata.create_all(engine)
