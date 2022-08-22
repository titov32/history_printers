from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from hp.api_router import hp_api_router
from hp.html_router import hp_html_router


application = FastAPI(title="History Printers",
              description="""Этот проект был создан для учета принтеров,
               их хранения и передвижения""",
              version="0.3.1",
              terms_of_service="http://example.com/terms/",
              contact={
                  "name": "Евгений Титов",
                  #"url": "http://мой_юрл",
                  "email": "e.titov@stroyservis.com",
              })
application.mount("/static", StaticFiles(directory="static"), name="static")

application.include_router(hp_api_router)
application.include_router(hp_html_router)
