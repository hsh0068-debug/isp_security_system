from fastapi import FastAPI
from database import engine
import models

app = FastAPI()

# This creates all the tables in the database automatically
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "ISP Security System is running!"}