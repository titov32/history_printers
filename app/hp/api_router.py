from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from . import schemas
from . import accouting
from .db import get_db
from .utils.converter import convert_from_depart_to_store

hp_api_router = APIRouter(
    prefix='/API',
    tags=['API']
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


@hp_api_router.post("/{user_id}/history")
async def create_history_printer(user_id: int,
                                 history: schemas.HistoryBase,
                                 db: AsyncSession = Depends(get_db)):
    return await crud.create_history_printer(db, user_id, history)


@hp_api_router.post("/storehouse/replenishment")  # , response_model=schemas.Printer)
async def update_storehouse(positions: schemas.UpdateStoreHouseBase,
                            db: AsyncSession = Depends(get_db)):
    if positions.operation == 'replenishment':
        result = await accouting\
            .receipt_of_cartridges(db, store_house_list=positions.cartridges)
        return result
    if positions.operation == 'transfer_to_service':
        result = await accouting\
            .shipment_of_cartridges(db, store_house_list=positions)
        return result


@hp_api_router.post("/storehouse/department")  # , response_model=schemas.Printer)
async def update_department_cartridge(positions: schemas.UpdateDepartmentCartridge,
                                      db: AsyncSession = Depends(get_db)):

    if positions.operation == 'return_from_department':
        # up unused == false and down department
        await accouting.return_cartridge_from_departament(db, positions)

    if positions.operation == 'transfer_to_department_with_return':
        result = await accouting.put_cart_depart_with_return(db, positions)
        return result
