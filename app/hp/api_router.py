from fastapi import APIRouter, File, UploadFile
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.users import current_active_user
from . import crud
from . import schemas
from . import accouting
from .db import get_db
from .utils.converter import convert_from_depart_to_store
from typing import List

hp_api_router = APIRouter(
    prefix='/API',
    tags=['API'],
)


@hp_api_router.post("/users/")  # , response_model=schemas.User)
async def create_user(user: schemas.UserCreate,
                      db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Email already is registered")
    return await crud.create_user(db=db, user=user)


@hp_api_router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User is not found")
    return db_user


@hp_api_router.get("/users/")  # , response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100,
                     db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    dict_users = {}
    for user, items in users:
        if not dict_users.get(user.id):
            dict_users[user.id] = {'id': user.id,
                                   'is_active': user.is_active,
                                   'email': user.email}
            dict_users[user.id]['items'].append(items)
        else:
            dict_users[user.id]['items'].append(items)
    # TODO нужно переделать функцию чтения пользователей, убрать items
    return list(dict_users.values())


@hp_api_router.get(
    "/cartridge/{cartridge_id}")  # , response_model=schemas.Cartridge
async def read_cartridge(cartridge_id: int,
                         db: AsyncSession = Depends(get_db)):
    db_cartridge = await crud.get_cartridge_by_id(db, cartridge_id)
    if db_cartridge is None:
        raise HTTPException(status_code=404, detail="Cartridge is not found")
    return await db_cartridge


@hp_api_router.post("/model_printer/", response_model=schemas.ModelPrinter)
async def create_model_printer(printer: schemas.ModelPrinterCreate,
                               db: AsyncSession = Depends(get_db)):
    db_model = await crud.get_printer_by_model(db, model=printer.model)
    if db_model:
        raise HTTPException(status_code=400, detail="Model already registered")
    return await crud.create_model(db=db, printer=printer)


@hp_api_router.get("/model_printer/all")
async def get_all_models_printer(db: AsyncSession = Depends(get_db)):
    models = await crud.read_model_printers(db)
    return models


@hp_api_router.put("/model_printer/", response_model=schemas.ModelPrinter)
async def edit_model_printer(printer: schemas.ModelPrinter,
                             db: AsyncSession = Depends(get_db)):
    db_model_printer = await crud.get_model_printer_by_id(db, printer.id)
    if db_model_printer is None:
        raise HTTPException(status_code=404,
                            detail="Model printer is not found")
    return await crud.update_model_printer(db, printer)


@hp_api_router.delete("/model_printer/{id_}")
async def remove_model_printer(id_: int,
                               db: AsyncSession = Depends(get_db)):
    return await crud.delete_model_printer(db=db, id_=id_)


@hp_api_router.post("/printer/")  # , response_model=schemas.Printer)
async def create_printer(printer: schemas.PrinterCreate,
                         db: AsyncSession = Depends(get_db)):
    db_printer = await crud.get_printer_by_sn(db, printer.sn)
    if db_printer:
        raise HTTPException(status_code=400,
                            detail="Printer already registered")
    printer_id = await crud.get_model_printer_by_id(db, id_=printer.model_id)
    if not printer_id:
        raise HTTPException(status_code=400,
                            detail='Model printer is not exist')

    created_printer = await crud.create_printer(db=db, printer=printer)

    return created_printer


@hp_api_router.put("/printer/", response_model=schemas.Printer)
async def update_printer(printer: schemas.Printer,
                         db: AsyncSession = Depends(get_db)):
    db_printer = await crud.get_printer_by_id(db, printer.id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    return await crud.update_printer(db, printer)


@hp_api_router.delete("/printer/")
async def delete_printer(printer: schemas.Printer,
                         db: AsyncSession = Depends(get_db)):
    return await crud.delete_printer(db, printer.id)


@hp_api_router.get("/printer/{printer_id}")
async def read_printer(printer_id: int, db: AsyncSession = Depends(get_db)):
    db_printer = await crud.get_printer_by_id_with_history(db, printer_id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    return db_printer


@hp_api_router.get("/printer/not_work")
async def get_not_work_printer(db: AsyncSession = Depends(get_db)):
    printers = await crud.get_report_printer_not_work(db)
    return printers


@hp_api_router.post("/history")
async def create_history_printer(history: schemas.HistoryBase,
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(current_active_user)):
    return await crud.create_history_printer(db, user.id, history)


@hp_api_router.post(
    "/storehouse/replenishment")  # , response_model=schemas.Printer)
async def update_storehouse(positions: schemas.UpdateStoreHouseBase,
                            db: AsyncSession = Depends(get_db),
                            user: User = Depends(current_active_user)):
    print(user)
    if user.is_active:
        if positions.operation == 'replenishment':
            result = await accouting \
                .receipt_of_cartridges(db,
                                       store_house_list=positions.cartridges)
            return result
        if positions.operation == 'transfer_to_service':
            result = await accouting \
                .shipment_of_cartridges(db, store_house_list=positions)
            return result
    else:
        raise HTTPException(status_code=403,
                            detail="Forbidden, need right for this operation")


@hp_api_router.post(
    "/storehouse/department")  # , response_model=schemas.Printer)
async def update_department_cartridge(
        positions: schemas.UpdateDepartmentCartridge,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(current_active_user)):
    if user.is_active:
        if positions.operation == 'return_from_department':
            # up unused == false and down department
            # повышыем использованные и уменьшеаем кол-во у отдела
            await accouting.return_cartridge_from_departament(db, positions)

        if positions.operation == 'transfer_to_department_with_return':
            result = await accouting.put_cart_depart_with_return(db, positions)
            return result
        if positions.operation == 'replace':
            print(positions.operation)
            await accouting.replace_cartridge_departament(db, positions)
    else:
        raise HTTPException(status_code=403,
                            detail="Forbidden, need right for this operation")


@hp_api_router.post("/department/")  # , response_model=schemas.Printer)
async def create_department(depart: schemas.DepartmentBase,
                            db: AsyncSession = Depends(get_db)):
    created_depart = await crud.create_department(db=db, department=depart)
    return created_depart


@hp_api_router.post("/uploadfile/")
async def create_upload_file(history: schemas.HistoryBase = Depends(),
                             files: List[UploadFile] = File(...),
                             user: User = Depends(current_active_user)):
    #TODO Нужно поменять endpoint на history и сделать запись в БД
    if user.is_active:

        return {
            "user": user.email,
            "JSON Payload ": history.dict(),
            "Filenames": [file.filename for file in files],
        }
    else:
        raise HTTPException(status_code=403,
                            detail="Forbidden, need right for this operation")
