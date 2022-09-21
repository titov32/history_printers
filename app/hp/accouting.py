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
                                        cartridge: schemas.Cartridge):
    # TODO нужно реализовать замену картриджа на заправку
    # Понизить счетчик в StoreHouse unused=True
    # TODO повысить счетчик в StoreHouse unused=False только для переиспользуемых картриджей
    pass


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
