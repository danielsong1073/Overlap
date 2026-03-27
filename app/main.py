from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routers import users, entries, connections

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(entries.router)
app.include_router(connections.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Overlap"}
