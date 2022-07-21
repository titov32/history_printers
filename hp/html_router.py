from fastapi import APIRouter, Request, Form
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from hp import crud
from hp import schemas
from hp.db import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from asyncpg.exceptions import ForeignKeyViolationError
from sqlalchemy.exc import IntegrityError

hp_html_router = APIRouter(
    prefix='',
    tags=['html'],
)

templates = Jinja2Templates(directory="static/templates")


@hp_html_router.get("/", response_class=HTMLResponse)
async def welcome(request: Request,
                  db: AsyncSession = Depends(get_db)):
    report_dont_work_printers = await crud.get_report_printer_not_work(db)
    report_repairing_printers = await crud.get_report_printer_in_repair(db)
    report_free_printers = await crud.get_report_printer_free(db)
    context = {"request": request,
               'report_dont_work_printers': report_dont_work_printers,
               'report_repairing_printers': report_repairing_printers,
               'report_free_printers': report_free_printers
               }
    return templates.TemplateResponse("index.html", context)


@hp_html_router.get("/models_printer", response_class=HTMLResponse)
async def get_all_models_printer(request: Request,
                                 db: AsyncSession = Depends(get_db)):
    models = await crud.read_model_printers(db)

    return templates.TemplateResponse("models_printer.html",
                                      {"request": request, "models": models})


@hp_html_router.post("/models_printer", response_class=HTMLResponse)
async def create_model_printer(request: Request,
                               brand=Form(),
                               model=Form(),
                               type_p=Form(),
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


@hp_html_router.get("/erase_model/{id}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id: int,
                                   db: AsyncSession = Depends(get_db)):
    printer = await crud.delete_model_printer(db, id)
    return RedirectResponse("/models_printer")


@hp_html_router.get("/printer/{id}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id: int,
                                   db: AsyncSession = Depends(get_db)):
    printer = await crud.get_printer_by_id_with_history(db, id)

    return templates.TemplateResponse("printer_with_history.html",
                                      {"request": request,
                                       "printers": printer})


@hp_html_router.get("/printers", response_class=HTMLResponse)
async def get_all_printers(request: Request,
                           db: AsyncSession = Depends(get_db)):
    printers = await crud.get_all_printers(db)
    return templates.TemplateResponse("printers.html",
                                      {"request": request,
                                       "printers": printers})


@hp_html_router.post("/printers", response_class=HTMLResponse)
async def create_printer(request: Request,
                         model_id=Form(),
                         departament=Form(),
                         ip=Form(),
                         sn=Form(),
                         is_work=Form(),
                         is_free=Form(),
                         repairing=Form(),
                         db: AsyncSession = Depends(get_db)):
    printer = schemas.PrinterCreate(model_id=model_id,
                                    departament=departament,
                                    ip=ip,
                                    sn=sn,
                                    is_work=is_work,
                                    is_free=is_free,
                                    repairing=repairing
                                    )
    try:
        await crud.create_printer(db, printer=printer)
    except ForeignKeyViolationError:
        print('ERROR!!!')
        # TODO нужно обработать исключение, к примеру перевести на форму и создать новую модель

    except Exception as e:
        print(f'Не обработанная ошибка {e}')
    printers = await crud.get_all_printers(db)
    return templates.TemplateResponse("printers.html",
                                      {"request": request,
                                       "printers": printers})


@hp_html_router.get("/erase_printer/{id}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id: int,
                                   db: AsyncSession = Depends(get_db)):
    printer = await crud.delete_printer(db, id)
    return RedirectResponse("/printers")


@hp_html_router.post("/printer/{id_}", response_class=HTMLResponse)
async def create_record_for_printer(request: Request, id_: int,
                                    description=Form(),
                                    db: AsyncSession = Depends(get_db)):
    record = schemas.HistoryBase(description=description, printer_id=id_)
    user_id = 1
    print(description)
    await crud.create_history_printer(db, user_id, record)
    printer = await crud.get_printer_by_id_with_history(db, id_)

    return templates.TemplateResponse("printer_with_history.html",
                                      {"request": request,
                                       "printers": printer})
