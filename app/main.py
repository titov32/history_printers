from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.hp.api_router import hp_api_router
from app.hp.html_router import hp_html_router
from app.hp.utils.logger import logger



app = FastAPI(title="History Printers",
              description="""Этот проект был создан для учета принтеров,
               их хранения и передвижения""",
              version="0.3.1",
              terms_of_service="http://example.com/terms/",
              contact={
                  "name": "Евгений Титов",
                  # "url": "http://мой_юрл",
                  "email": "e.titov@stroyservis.com",
              })
app.mount("/app/static", StaticFiles(directory="app/static"), name="app/static")

app.include_router(hp_api_router)
app.include_router(hp_html_router)

@app.on_event("startup")
async def on_startup():

    logger.info('app startup')


@app.on_event("shutdown")
async def on_startup():
    logger.info('app shutdown')