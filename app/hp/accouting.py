from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from .utils.converter import convert_from_store_to_depart, \
    convert_from_depart_to_store
from app.hp import schemas
from app.hp import crud
from sqlalchemy.dialects.postgresql import insert


async def commit_record(db: AsyncSession,
                        records: list):
    for record in records:
        await db.execute(record)
    return await db.commit()


async def return_cartridge_from_departament(db: AsyncSession,
                                            positions: schemas.UpdateDepartmentCartridge):
    """Реализация возврата картриджа на заправку"""
    # повысить счетчик в StoreHouse
    schema = convert_from_depart_to_store(positions,
                                          unused=False,
                                          operation='+')
    records = crud.upsert_in_store_house(schema.cartridges)
    # понизить счетчик в CounterCartridge
    for cart in positions.cartridges:
        cart.amount = -cart.amount
    records.extend(crud.upsert_counter_cartridge(positions.cartridges))
    await commit_record(db, records=records)


async def replace_cartridge_departament(db: AsyncSession,
                                        depart_cart_list: schemas.UpdateDepartmentCartridge):
    # Реализация замены картриджа на заправку Понизить счетчик в StoreHouse
    # unused=True повысить счетчик в StoreHouse unused=False только для
    # переиспользуемых картриджей
    sh_schema = convert_from_depart_to_store(depart_cart_list,
                                             unused=True,
                                             operation='-')
    records = crud.upsert_in_store_house(sh_schema.cartridges)

    id_cart = []
    for cartridge in depart_cart_list.cartridges:
        id_cart.append(cartridge.id_cartridge)

    id_cart_reused = await crud.get_all_id_reused_cartridges(db, id_cart)
    reused = schemas.UpdateDepartmentCartridge(
        operation=depart_cart_list.operation,
        cartridges=[cartridge for cartridge in depart_cart_list.cartridges if
                    cartridge.id_cartridge in id_cart_reused])
    sh_schema = convert_from_depart_to_store(depart_cart_list,
                                             unused=False,
                                             operation='+')
    records.extend(crud.upsert_in_store_house(sh_schema.cartridges))
    result = await commit_record(db, records=records)
    print(result)
    return result
    # raise NotImplementedError


async def put_cartridge_departament(db: AsyncSession,
                                    cartridge: schemas.Cartridge):
    # TODO нужно реализовать передачу картриджа на отделу без возврата
    # down storehouse unused==True
    pass


async def put_cart_depart_with_return(db: AsyncSession,
                                      store_house_list: schemas.UpdateDepartmentCartridge):
    # TODO нужно реализовать передачу картриджа отделу c возвратом
    # нужно повысить счетчик отдела и понизить счетчик на складе
    records = crud.upsert_counter_cartridge(
        counter_cartridge=store_house_list.cartridges)
    schema = convert_from_depart_to_store(schema=store_house_list,
                                          unused=True,
                                          operation='-')
    records.extend(crud.upsert_in_store_house(schema.cartridges))
    await commit_record(db, records=records)


async def shipment_of_cartridges(db: AsyncSession,
                                 store_house_list: schemas.UpdateStoreHouseBase):
    # отправка картриджей на заправку
    # Нужно обработать ошибку отсутствия сервисного отдела
    # up department_id==service and down unused==False
    service_depart = await crud.get_service_department(db)
    if not service_depart:
        raise ValueError('Department "service" is not found')
    depart_cartridge = convert_from_store_to_depart(schema=store_house_list,
                                                    department_id=service_depart,
                                                    operation='+')
    records = crud.upsert_counter_cartridge(depart_cartridge.cartridges)
    for item in store_house_list.cartridges:
        item.amount = -item.amount
    records.extend(crud.upsert_in_store_house(store_house_list.cartridges))
    await commit_record(db, records=records)


async def receipt_of_cartridges(db: AsyncSession,
                                store_house_list: [schemas.StoreHouseBase]):
    # Добавление картриджа на складе
    records = crud.upsert_in_store_house(store_house_list)
    await commit_record(db, records=records)


async def report_cartridges_on_storehouse_unused(db: AsyncSession,
                                                 cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам
    pass


async def report_cartridges_on_storehouse_used(db: AsyncSession,
                                               cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам требующих заправки
    pass


async def report_cartridges_with_model(db: AsyncSession,
                                       cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам по моделям принтеров
    pass


async def update_history_printer(db: AsyncSession,
                                 printer_id: int,
                                 printer_update: schemas.PrinterUpdate,
                                 user_id: UUID):
    prn = await crud.get_printer_by_id(db, printer_id)
    prn = prn[0]
    printer_new = printer_update.printer
    printer_old = schemas.PrinterBase(department_id=prn.department_id,
                                      ip=prn.ip,
                                      sn=prn.sn,
                                      connection=prn.connection,
                                      condition=prn.condition,
                                      model_id=prn.model_id,
                                      location=prn.location, )
    notice = ''

    if printer_new.location != printer_old.location:
        notice += f'Принтер перехал из {printer_old.location}' \
                  f' в {printer_new.location} '
    if printer_new.connection != printer_old.connection:
        if printer_new.connection == 'USB':
            notice += f'Принтер переключили на USB '
        else:
            notice += f'Принтер подключили к ЛВС'
    if printer_new.ip:
        notice += f'Принтер получил IP адрес на {printer_new.ip} '
    if printer_new.condition != printer_old.condition:
        notice += f'Принтер стал изменил состояние на {printer_new.condition.value} '

    notice = f'{printer_update.description} {notice}'
    record = schemas.HistoryBase(description=notice,
                                 printer_id=printer_id)
    return await crud.update_printer_with_history(db,
                                           printer_new,
                                           printer_id,
                                           record,
                                           user_id)
