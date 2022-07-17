from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hp.api_router import hp_api_router


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(hp_api_router)








