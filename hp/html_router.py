from fastapi import APIRouter, Request, Form
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from hp import crud
from hp import schemas
from hp.db import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

hp_html_router = APIRouter(
    prefix=''
)

templates = Jinja2Templates(directory="static/templates")

@hp_html_router.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@hp_html_router.get("/models_printer", response_class=HTMLResponse)
async def get_all_models_printer(request: Request, db: AsyncSession = Depends(get_db)):
    models = await crud.read_model_printers(db)

    return templates.TemplateResponse("models_printer.html",
                                      {"request": request, "models": models})


@hp_html_router.post("/models_printer", response_class=HTMLResponse)
async def create_model_printer(request: Request,
                                brand=Form(),
                                model = Form(),
                               type_p = Form(),
                               format_paper=Form(),
                               db: AsyncSession = Depends(get_db)):
    model = schemas.ModelPrinterCreate(brand=brand,
                                       model=model,
                                       type_p=type_p,
                                       format_paper=format_paper)
    await crud.create_model(db, model)
    models = await crud.read_model_printers(db)
    return templates.TemplateResponse("models_printer.html",
                                      {"request": request, "models": models})


@hp_html_router.get("/printer/{id}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id: int, db: AsyncSession = Depends(get_db)):
    printer = await crud.get_printer_by_id_with_history(db, id)
    # TODO нужно доработать шаблон для принтера с историей
    return templates.TemplateResponse("printer_with_history.html",
                                      {"request": request, "printers": printer})


@hp_html_router.get("/printers", response_class=HTMLResponse)
async def get_all_printers(request: Request, db: AsyncSession = Depends(get_db)):
    printers = await crud.get_all_printers(db)
    return templates.TemplateResponse("printers.html",
                                      {"request": request, "printers": printers})

    #TODO нужно доработать форму заведения нового принтера