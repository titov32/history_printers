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
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from app.hp.utils.logger import log_api_route, logger
from .utils.foto import get_address

hp_api_router = APIRouter(
    prefix='/API0',
    tags=['API0'],
)

router = InferringRouter(tags=['API'], prefix='/API', )


@cbv(router)
class ModelCBV:
    db: AsyncSession = Depends(get_db)

    @router.post("/model_printer/", response_model=schemas.ModelPrinter)
    async def create_model_printer(self, printer: schemas.ModelPrinterCreate):
        db_model = await crud.get_printer_by_model(self.db, model=printer.model)
        if db_model:
            raise HTTPException(status_code=400, detail="Model already registered")
        return await crud.create_model(db=self.db, printer=printer)

    @router.get("/model_printer/all")
    async def get_all_models_printer(self):
        models = await crud.read_model_printers(self.db)
        return models

    @router.put("/model_printer/", response_model=schemas.ModelPrinter)
    async def edit_model_printer(self, printer: schemas.ModelPrinter):
        db_model_printer = await crud.get_model_printer_by_id(self.db, printer.id)
        if db_model_printer is None:
            raise HTTPException(status_code=404,
                                detail="Model printer is not found")
        return await crud.update_model_printer(self.db, printer)

    @router.delete("/model_printer/{id_}")
    async def remove_model_printer(self, id_: int):
        return await crud.delete_model_printer(db=self.db, id_=id_)


@cbv(router)
class PrinterCBV:
    db: AsyncSession = Depends(get_db)

    @router.post("/printer/")  # , response_model=schemas.Printer)
    async def create_printer(self, printer: schemas.PrinterCreate):
        # TODO разрешить только авторизированному пользователю
        db_printer = await crud.get_printer_by_sn(self.db, printer.sn)
        if db_printer:
            raise HTTPException(status_code=400,
                                detail="Printer already registered")
        printer_id = await crud.get_model_printer_by_id(self.db, id_=printer.model_id)
        if printer.connection.usb and printer.ip:
            raise HTTPException(status_code=400,
                                detail='Choise connection ip or USB')
        if printer.connection.ip and not printer.ip:
            raise HTTPException(status_code=400,
                                detail='Need write IP address')
        if not printer_id:
            raise HTTPException(status_code=400,
                                detail='Model printer is not exist')
        created_printer = await crud.create_printer(db=self.db, printer=printer)
        return created_printer

    @router.put("/printer/", response_model=schemas.Printer)
    async def update_printer(self, printer: schemas.Printer):
        # TODO разрешить только авторизированному пользователю
        db_printer = await crud.get_printer_by_id(self.db, printer.id)
        if db_printer is None:
            raise HTTPException(status_code=404, detail="Printer is not found")
        return await crud.update_printer(self.db, printer)

    @router.delete("/printer/")
    async def delete_printer(self, printer: schemas.Printer, ):
        # TODO разрешить удалять принтеры только админу
        return await crud.delete_printer(self.db, printer.id)

    @router.get("/printer/{printer_id}")
    async def read_printer(self, printer_id: int, ):
        db_printer = await crud.get_printer_by_id_with_history(self.db, printer_id)
        if db_printer is None:
            raise HTTPException(status_code=404, detail="Printer is not found")
        return db_printer


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


@hp_api_router.get("/printer/not_work")
async def get_not_work_printer(db: AsyncSession = Depends(get_db)):
    printers = await crud.get_report_printer_not_work(db)
    return printers


@cbv(router)
class HistoryCBV:
    db: AsyncSession = Depends(get_db)
    user: User = Depends(current_active_user)

    @router.post("/history")
    async def create_history_printer(self,
                                     history: schemas.HistoryBase = Depends(),
                                     files: List[UploadFile] = File(...),):
        if self.user.is_active:
            files = [file for file in files]
            for file in files:
                log_api_route.debug(f'files: {file}')
                file_location = f"app/static/img/{file.filename}"
                history.path_file = file_location
                with open(file_location, "wb+") as file_object:
                    file_object.write(file.file.read())
                    try:
                        coordinate = get_address(file_location)
                        address = coordinate.get('address')
                        history.latitude = coordinate.get('latitude')
                        history.longitude = coordinate.get('longitude')
                        if address:
                            history.description += f'Адрес: {address}'
                    except Exception as e:
                        print(e)
        else:
            raise HTTPException(status_code=403,
                                detail="Forbidden, need right for this operation")
        log_api_route.info(f'Create record {self.user.email} ::: {history.description}')
        return await crud.create_history_printer(self.db, self.user.id, history)

    @router.put('/history/{printer_id}')
    async def update_history_printer(self,
                                     printer_id: int,
                                     printer: schemas.PrinterUpdate,):
        if self.user.is_active:
            log_api_route.info(f'Update record {self.user.email} ::: {printer.description}')
            return await accouting.update_history_printer(self.db,
                                                          printer_id,
                                                          printer_update=printer,
                                                          user_id=self.user.id, )
        else:
            raise HTTPException(status_code=403,
                                detail="Forbidden, need right for this operation")

    @router.delete('/history/{printer_id}')
    async def erase_history_printer(self, printer_id: int, ):
        pass


@cbv(router)
class StoreHouseCBV:
    db: AsyncSession = Depends(get_db)
    user: User = Depends(current_active_user)

    @router.post("/storehouse/replenishment")
    async def update_storehouse(self,
                                positions: schemas.UpdateStoreHouseBase,
                                ):
        logger.info(f'user post {self.user.email}')
        if self.user.is_active:
            if positions.operation == 'replenishment':
                log_api_route.info(f'user {self.user.email} осуществил поступление картриджей {positions.cartridges}')
                result = await accouting \
                    .receipt_of_cartridges(self.db,
                                           store_house_list=positions.cartridges)
                return result
            if positions.operation == 'transfer_to_service':
                log_api_route.info(f'user {self.user.email} осуществил передачу в сервис {positions.cartridges}')
                result = await accouting \
                    .shipment_of_cartridges(self.db, store_house_list=positions)
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


@hp_api_router.post("/storehouse/department")  # , response_model=schemas.Printer)
async def update_department_cartridge(positions: schemas.UpdateDepartmentCartridge,
                                      db: AsyncSession = Depends(get_db)):
    if positions.operation == 'return_from_department':
        # up unused == false and down department
        await accouting.return_cartridge_from_departament(db, positions)

    if positions.operation == 'transfer_to_department_with_return':
        result = await accouting.put_cart_depart_with_return(db, positions)
        return result
    if positions.operation == 'replace':
        print(positions.operation)
        await accouting.replace_cartridge_departament(db, positions)


@hp_api_router.post("/department/")  # , response_model=schemas.Printer)
async def create_department(depart: schemas.DepartmentBase,
                            db: AsyncSession = Depends(get_db)):
    created_depart = await crud.create_department(db=db, department=depart)
    return created_depart
