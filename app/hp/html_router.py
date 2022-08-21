from typing import Union, List

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from . import crud
from . import schemas
from .db import get_db
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
               'report_free_printers': report_free_printers,
               'main_active': 'active'
               }
    return templates.TemplateResponse("index.html", context)


@hp_html_router.get("/models_printer", response_class=HTMLResponse)
async def get_all_models_printer(request: Request,
                                 db: AsyncSession = Depends(get_db)):
    models = await crud.read_model_printers(db)
    models_with_cartridges = await crud.read_model_with_cartridges(db)
    context = {"request": request, "models": models,
               "models_with_cartridges": models_with_cartridges,
               "models_printer_active": "active"}
    print(models)
    print(models_with_cartridges)
    return templates.TemplateResponse("models_printer.html", context)


@hp_html_router.post("/models_printer", response_class=HTMLResponse)
async def create_model_printer(brand=Form(),
                               model=Form(),
                               type_p=Form(),
                               format_paper=Form(),
                               db: AsyncSession = Depends(get_db)):
    model = schemas.ModelPrinterCreate(brand=brand,
                                       model=model,
                                       type_p=type_p,
                                       format_paper=format_paper)
    await crud.create_model(db, model)
    print(Form())
    return RedirectResponse(url=f'/models_printer', status_code=302)


@hp_html_router.get("/erase_model/{id}", response_class=HTMLResponse)
async def delete_printer(request: Request, id: int,
                         db: AsyncSession = Depends(get_db)):
    printer = await crud.delete_model_printer(db, id)
    return RedirectResponse("/models_printer")


@hp_html_router.get("/printer/{id_}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id_: int,
                                   db: AsyncSession = Depends(get_db)):
    printer = await crud.get_printer_by_id_with_history(db, id_)
    context = {"request": request,
               "printers": printer,
               "printer_active": "active"}
    return templates.TemplateResponse("printer_with_history.html", context)


@hp_html_router.get("/printers", response_class=HTMLResponse)
async def get_all_printers(request: Request,
                           db: AsyncSession = Depends(get_db)):
    printers = await crud.get_all_printers(db)
    departments = await crud.get_departments(db)
    context = {"request": request,
               "printers": printers,
               "departments": departments,
               "printer_active": "active"}
    return templates.TemplateResponse("printers.html", context)


@hp_html_router.get("/printers/{model_id}", response_class=HTMLResponse)
async def get_all_printers_by_model(request: Request, model_id: int,
                                    db: AsyncSession = Depends(get_db)):
    printers = await crud.get_printers_by_model_id(db, model_id=model_id)
    departments = await crud.get_departments(db)

    context = {"request": request,
               "printers": printers,
               "model_id": model_id,
               "departments": departments,
               "printer_active": "active"}
    return templates.TemplateResponse("printers_model_id.html", context)


@hp_html_router.post("/printers/{model_id}", response_class=HTMLResponse)
async def create_printer(model_id: int,
                         department_id=Form(),
                         ip=Form(),
                         sn=Form(),
                         location=Form(),
                         is_work=Form(),
                         is_free=Form(),
                         repairing=Form(),
                         db: AsyncSession = Depends(get_db)):
    # TODO Нужно проверить и обработать ошибку 404
    printer = schemas.PrinterCreate(model_id=model_id,
                                    department_id=department_id,
                                    ip=ip,
                                    sn=sn,
                                    location=location,
                                    is_work=is_work,
                                    is_free=is_free,
                                    repairing=repairing
                                    )
    if await crud.get_printer_by_sn(db, sn):
        raise HTTPException(status_code=400, detail='Дубликат sn')

    if not await crud.get_model_printer_by_id(db, id_=int(model_id)):
        raise HTTPException(status_code=400, detail='неверное указана модель')

    try:
        await crud.create_printer(db, printer=printer)
    except Exception as e:
        print(f'Не обработанная ошибка {e}')

    return RedirectResponse(url=f'/printers/{model_id}', status_code=302)


@hp_html_router.get("/printers/department/{department}",
                    response_class=HTMLResponse)
async def get_all_printers_by_model(request: Request, departament: int,
                                    db: AsyncSession = Depends(get_db)):
    printers = await crud.get_printers_by_departament(db,
                                                      department=departament)
    context = {"request": request,
               "printers": printers,
               "departament": departament,
               "printer_active": "active"}
    return templates.TemplateResponse("printers_model_id.html", context
                                      )


@hp_html_router.get("/erase_printer/{id}", response_class=HTMLResponse)
async def get_printer_with_history(request: Request, id: int,
                                   db: AsyncSession = Depends(get_db)):
    printer = await crud.delete_printer(db, id)
    return RedirectResponse("/printers")


@hp_html_router.post("/printer/{id_}", response_class=HTMLResponse)
async def create_record_for_printer(request: Request, id_: int,
                                    description=Form(),
                                    files: List[UploadFile] = File(
                                        description="Multiple files as UploadFile"),
                                    db: AsyncSession = Depends(get_db)):
    # TODO Нужно заменить user_id
    # TODO Нужно обработать ошибку 404
    user_id = 1
    if not files[0].filename:
        path_file = None
    else:
        files = [file for file in files]
        path_file = ''
        for file in files:
            file_location = f"static/img/{file.filename}"
            path_file += file_location
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
    record = schemas.HistoryBase(description=description,
                                 printer_id=id_,
                                 path_file=path_file)
    await crud.create_history_printer(db, user_id, record)

    return RedirectResponse(url=f'/printer/{id_}', status_code=302)


@hp_html_router.get("/update_printer/{id_}", response_class=HTMLResponse)
async def get_form_for_update_printer(request: Request, id_: int,
                                      db: AsyncSession = Depends(get_db)):
    user_id = 1
    printer = await crud.get_printer_by_id(db, id_)
    departments = await crud.get_departments(db)
    context = {"request": request,
               "printer": printer[0],
               "departments": departments}
    return templates.TemplateResponse("update_printer.html", context)


@hp_html_router.post("/update_printer/{id_}", response_class=HTMLResponse)
async def update_printer(request: Request, id_: int,
                         db: AsyncSession = Depends(get_db),
                         department=Form(),
                         ip=Form(),
                         is_work=Form(),
                         is_free=Form(),
                         repairing=Form(),
                         description=Form(),
                         location=Form()
                         ):
    user_id = 1
    prn = await crud.get_printer_by_id(db, id_)
    prn = prn[0]
    printer_old = schemas.PrinterUpdate(department_id=prn.department_id,
                                        ip=prn.ip,
                                        sn=prn.sn,
                                        is_work=prn.is_work,
                                        is_free=prn.is_free,
                                        repairing=prn.repairing,
                                        model_id=prn.model_id,
                                        id=prn.id,
                                        location=prn.location, )
    printer_new = schemas.PrinterUpdate(department_id=department,
                                        ip=ip,
                                        sn=prn.sn,
                                        is_work=is_work,
                                        is_free=is_free,
                                        repairing=repairing,
                                        model_id=prn.model_id,
                                        id=id_,
                                        location=location)
    notice = ''
    if printer_new.department_id != printer_old.department_id:
        notice += f'Принтер перехал из {printer_old.department.name} в {printer_new.department.name}'
    if printer_new.ip.ip.exploded != printer_old.ip.ip.exploded:
        notice += f'Принтер сменил IP адрес на {printer_new.ip}'
    if printer_new.location != printer_old.location:
        notice += f'Принтер перехал из {printer_old.location} в {printer_new.location}'
    if printer_new.is_work != printer_old.is_work:
        if printer_old.is_work:
            notice += f'Принтер перестал работать'
        else:
            notice += f'Принтер заработал'
    if printer_new.is_free != printer_old.is_free:
        if printer_old.is_free:
            notice += f'Принтер стал использоваться'
        else:
            notice += f'Принтер освободился'
    if printer_new.repairing != printer_old.repairing:
        if printer_old.repairing:
            notice += f'Принтер отремонтирован'
        else:
            notice += f'Принтер уехал в ремонт'

    notice = f'{description} {notice}'
    record = schemas.HistoryBase(description=notice,
                                 printer_id=id_)
    await crud.update_printer_with_history(db, printer_new, record, user_id)

    return RedirectResponse(url=f'/printer/{id_}', status_code=302)


@hp_html_router.get("/cartridges", response_class=HTMLResponse)
async def get_all_cartridges(request: Request,
                             db: AsyncSession = Depends(get_db)):
    cartridges = await crud.get_cartridges(db)
    context = {"request": request,
               "cartridges": cartridges,
               "cartridges_active": "active"}
    return templates.TemplateResponse("cartridges.html", context=context)


@hp_html_router.post("/cartridges", response_class=HTMLResponse)
async def create_cartridge(number=Form(),
                           db: AsyncSession = Depends(get_db)):
    cartridge = schemas.CartridgeBase(number=number)
    await crud.create_cartridge(db, cartridge)
    return RedirectResponse(url=f'/cartridges', status_code=302)


@hp_html_router.get("/cartridge_add/{id_}", response_class=HTMLResponse)
async def get_form_add_cartridges_to_model(request: Request,
                                           db: AsyncSession = Depends(get_db)):
    cartridges = await crud.get_cartridges(db)

    context = {"request": request,
               "cartridges": cartridges,
               "cartridges_active": "active",
               "button": "btn-primary",
               "text_button": "Добавить картридж"}
    return templates.TemplateResponse("add_cartridge_to_model.html", context)


@hp_html_router.post("/cartridge_add/{id_}", response_class=HTMLResponse)
async def get_form_add_cartridges_to_model(id_: int,
                                           cart=Form(),
                                           db: AsyncSession = Depends(get_db), ):
    await crud.add_cart_for_model(db, model=id_, cart=int(cart))

    return RedirectResponse(url=f'/models_printer', status_code=302)


@hp_html_router.get("/cartridge_delete/{id_}", response_class=HTMLResponse)
async def get_form_delete_cartridges_from_model(id_: int, request: Request,
                                                db: AsyncSession = Depends(get_db)):
    cartridges = await crud.get_cartridges_by_model_id(db, id_)

    context = {"request": request,
               "cartridges": cartridges,
               "cartridges_active": "active",
               "button": "btn-danger",
               "text_button": "Удалить картридж"}
    return templates.TemplateResponse("add_cartridge_to_model.html", context)


@hp_html_router.post("/cartridge_delete/{id_}", response_class=HTMLResponse)
async def get_form_add_cartridges_to_model(id_: int,
                                           cart=Form(),
                                           db: AsyncSession = Depends(get_db), ):
    await crud.delete_cart_for_model(db, model=id_, cart=int(cart))

    return RedirectResponse(url=f'/models_printer', status_code=302)


@hp_html_router.get("/departments", response_class=HTMLResponse)
async def get_all_departments(request: Request,
                              db: AsyncSession = Depends(get_db)):
    departments = await crud.get_departments(db)
    context = {"request": request, "departments": departments,
               "departments_active": "active"}
    return templates.TemplateResponse("departments.html", context)


@hp_html_router.post("/departments", response_class=HTMLResponse)
async def create_department(name=Form(),
                            company=Form(),
                            db: AsyncSession = Depends(get_db)):
    departament = schemas.DepartmentBase(name=name,
                                         company=company)
    await crud.create_department(db, departament)
    return RedirectResponse(url=f'/departments', status_code=302)
