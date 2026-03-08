from fastapi import FastAPI
from .database import database,create_tables
from prometheus_fastapi_instrumentator import Instrumentator
from .routers import (
    auth_router,
    users_router,
    book_router,
    progress_router,
    notes_router,
    analytics_router
)

app = FastAPI(title="Reading Tracker API")
Instrumentator().instrument(app).expose(app)

app.include_router(auth_router.router,prefix="/auth")
app.include_router(users_router.router)
app.include_router(book_router.router)
app.include_router(progress_router.router)
app.include_router(notes_router.router)
app.include_router(analytics_router.router)

@app.on_event("startup")
async def startup():
    create_tables()
    await database.connect()
    

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

     
            