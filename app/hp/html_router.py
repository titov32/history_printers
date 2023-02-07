from typing import List
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from . import crud
from . import schemas
from . import accouting
from .db import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .utils.xlsx import create_xlsx_file
from .utils.foto import get_address

hp_html_router = APIRouter(
    prefix='',
    tags=['html'],
)

templates = Jinja2Templates(directory="app/static/templates")


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
    return templates.TemplateResponse("report_printers.html", context)


@hp_html_router.get("/models_printer", response_class=HTMLResponse)
async def get_all_models_printer(request: Request,
                                 db: AsyncSession = Depends(get_db)):
    models_with_cartridges = await crud.read_model_with_cartridges(db)
    context = {"request": request,
               "models_with_cartridges": models_with_cartridges,
               "models_printer_active": "active"}
    return templates.TemplateResponse("models_printer.html", context)


@hp_html_router.post("/models_printer", response_class=HTMLResponse)
async def create_model_printer(request: Request,
                               brand=Form(),
                               model=Form(),
                               type_p=Form(),
                               format_paper=Form(),
                               db: AsyncSession = Depends(get_db)):
    # TODO обработать ошибку повторяющих значений

    model = schemas.ModelPrinterCreate(brand=brand,
                                       model=model,
                                       type_p=type_p,
                                       format_paper=format_paper)

    await crud.create_model(db, model)
    return RedirectResponse(url=f'/models_printer', status_code=302)


@hp_html_router.get("/erase_model/{id_}", response_class=HTMLResponse)
async def delete_printer(id_: int,
                         request: Request,
                         db: AsyncSession = Depends(get_db)):
    await crud.delete_model_printer(db, id_)
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
    context = {"request": request,
               "printers": printers,
               "printer_active": "active"}
    return templates.TemplateResponse("printers.html", context)


@hp_html_router.get("/get_excel_printer", response_class=HTMLResponse)
async def get_all_printers_for_excel(db: AsyncSession = Depends(get_db)):
    printers = await crud.get_all_printers(db)
    create_xlsx_file(printers)
    return RedirectResponse(url=f'/printers', status_code=302)


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
                         condition=Form(),
                         connection=Form(),
                         db: AsyncSession = Depends(get_db)):
    # TODO Нужно проверить и обработать ошибку 404
    if ip == '192.168.0.0' or connection == 'USB':
        ip = None
    printer = schemas.PrinterCreate(model_id=model_id,
                                    department_id=department_id,
                                    ip=ip,
                                    sn=sn,
                                    location=location,
                                    condition=condition,
                                    connection=connection,
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
async def get_all_printers_by_department(request: Request, department: int,
                                         db: AsyncSession = Depends(get_db)):
    printers = await crud.get_printers_by_departament(db,
                                                      department=department)
    depart = await crud.get_department_by_id(db, department)
    print()
    print(f'printers: {printers}')
    context = {"request": request,
               "printers": printers,
               "department": depart,
               "printer_active": "active"}
    return templates.TemplateResponse("printers_departments.html", context)


@hp_html_router.get("/erase_printer/{id_}", response_class=HTMLResponse)
async def get_printer_with_history(id_: int,
                                   db: AsyncSession = Depends(get_db)):
    await crud.delete_printer(db, id_)
    return RedirectResponse("/printers")


@hp_html_router.get("/update_printer/{id_}", response_class=HTMLResponse)
async def get_form_for_update_printer(request: Request, id_: int,
                                      db: AsyncSession = Depends(get_db)):
    printer = await crud.get_printer_by_id(db, id_)
    departments = await crud.get_departments(db)
    context = {"request": request,
               "printer": printer[0],
               "departments": departments}
    return templates.TemplateResponse("update_printer.html", context)


@hp_html_router.post("/update_printer/{id_}", response_class=HTMLResponse)
async def update_printer(id_: int,
                         db: AsyncSession = Depends(get_db),
                         department=Form(),
                         ip=Form(),
                         condition=Form(),
                         connection=Form(),
                         description=Form(),
                         location=Form()
                         ):
    user_id = "1ae7329b-1fea-4d91-8127-2d290f7cea0c"
    prn = (await crud.get_printer_by_id(db, id_))[0]
    printer_new = schemas.PrinterUpdate(department_id=department,
                                        ip=ip,
                                        sn=prn.sn,
                                        condition=condition,
                                        connection=connection,

                                        model_id=prn.model_id,
                                        id=id_,
                                        location=location)
    await accouting.update_history_printer(db,
                                           printer_id=id_,
                                           description=description,
                                           printer_new=printer_new,
                                           user_id=user_id)
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
                           reused=Form(),
                           db: AsyncSession = Depends(get_db)):
    if reused == "Да":
        reused = True
    else:
        reused = False
    cartridge = schemas.CartridgeBase(number=number, reused=reused)
    await crud.create_cartridge(db, cartridge)
    return RedirectResponse(url=f'/cartridges', status_code=302)


@hp_html_router.get("/update_cartridge/{id_}", response_class=HTMLResponse)
async def get_form_for_update_cartridge(request: Request, id_: int,
                                        db: AsyncSession = Depends(get_db)):
    cartridge = await crud.get_cartridge_by_id(db, id_)

    context = {"request": request,
               "cartridge": cartridge}
    return templates.TemplateResponse("update_cartridge.html", context)


@hp_html_router.post("/update_cartridge/{id_}", response_class=HTMLResponse)
async def create_cartridge(id_: int,
                           number=Form(),
                           reused=Form(),
                           db: AsyncSession = Depends(get_db)):
    if reused == "Да":
        reused = True
    else:
        reused = False
    cartridge = schemas.Cartridge(number=number, reused=reused, id=id_)
    await crud.update_cartridge(db, cartridge)
    return RedirectResponse(url=f'/cartridges', status_code=302)


@hp_html_router.get("/erase_cartridge/{id_}", response_class=HTMLResponse)
async def delete_cartridge(id_: int,
                           db: AsyncSession = Depends(get_db)):
    await crud.delete_cartridge(db, id_)
    return RedirectResponse("/cartridges")


@hp_html_router.get("/cartridge_add/{id_}", response_class=HTMLResponse)
async def get_form_add_cartridges_to_model(request: Request, id_,
                                           db: AsyncSession = Depends(get_db)):
    cartridges = await crud.get_cartridges_unlinked(db, model_id=int(id_))

    context = {"request": request,
               "cartridges": cartridges,
               "cartridges_active": "active",
               "button": "btn-primary",
               "text_button": "Добавить картридж"}
    return templates.TemplateResponse("add_cartridge_to_model.html", context)


@hp_html_router.post("/cartridge_add/{id_}", response_class=HTMLResponse)
async def get_form_add_cartridges_to_model(id_: int,
                                           cart=Form(),
                                           db: AsyncSession = Depends(
                                               get_db), ):
    await crud.upsert_cart_for_model(db, model=id_, cart=int(cart))

    return RedirectResponse(url=f'/models_printer', status_code=302)


@hp_html_router.get("/cartridge_delete/{id_}", response_class=HTMLResponse)
async def get_form_delete_cartridges_from_model(id_: int, request: Request,
                                                db: AsyncSession = Depends(
                                                    get_db)):
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
                                           db: AsyncSession = Depends(
                                               get_db), ):
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
                            service=Form(),
                            db: AsyncSession = Depends(get_db)):
    department = schemas.DepartmentBase(name=name,
                                        company=company,
                                        service=service)
    await crud.create_department(db, department)
    return RedirectResponse(url=f'/departments', status_code=302)


@hp_html_router.get("/storehouse", response_class=HTMLResponse)
async def get_storehouse(request: Request,
                         db: AsyncSession = Depends(get_db)):
    sh_unused = await crud.get_all_cartridges_in_store_house(db,
                                                             unused=True)
    sh_used = await crud.get_all_cartridges_in_store_house(db,
                                                           unused=False)
    cartridges = await crud.get_cartridges(db)
    context = {"request": request,
               "storehouse_unused": sh_unused,
               "storehouse_used": sh_used,
               "cartridges": cartridges,
               }
    return templates.TemplateResponse("storehouse.html", context)


@hp_html_router.get("/storehouse/replenishment", response_class=HTMLResponse)
async def get_form_storehouse_replenishment(request: Request,
                                            db: AsyncSession = Depends(
                                                get_db)):
    cartridges = await crud.get_cartridges(db)
    context = {"request": request,
               "cartridges": cartridges,
               }
    return templates.TemplateResponse("form_storehouse_replenishment.html",
                                      context)


@hp_html_router.get("/counter_departs", response_class=HTMLResponse)
async def get_storehouse(request: Request,
                         db: AsyncSession = Depends(get_db)):
    count_departs = await crud.get_all_cartridges_in_departments(db)
    departments = await crud.get_departments(db)
    cartridges = await crud.get_cartridges(db)
    context = {"request": request,
               "count_departs": count_departs,
               "cartridges": cartridges,
               "departments": departments
               }
    return templates.TemplateResponse("counter_department.html", context)


@hp_html_router.get("/report/cartridges/{cartridge_id}", response_class=HTMLResponse)
async def get_storehouse(request: Request,
                         cartridge_id: str,
                         db: AsyncSession = Depends(get_db)):
    list_department = await crud.get_list_depart_use_cart(db, int(cartridge_id))
    if list_department is None:
        raise HTTPException(status_code=404, detail="No department use this cartdige")
    all_quaintity_cartridge = await crud.get_sum_all_by_id_cart(db, int(cartridge_id))
    storehouse = await crud.get_sum_all_by_id_cart_in_storehouse(db,
                                                                 cartridge_id)
    depart = await crud.get_all_by_id_cart_in_departs(db, cartridge_id)
    cart_in_service = await  crud.get_used_cart(db, cartridge_id)
    context = {"request": request,
               "list_department": list_department,
               "all_quaintity_cartridge": all_quaintity_cartridge,
               "storehouse":storehouse,
               "depart":depart,
               "cart_in_service":cart_in_service
               }
    return templates.TemplateResponse("report_cartridge.html", context)
