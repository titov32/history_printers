from sqlalchemy.ext.asyncio import AsyncSession
from .utils.converter import convert_from_store_to_depart, convert_from_depart_to_store
from app.hp import schemas
from app.hp import crud
from sqlalchemy.dialects.postgresql import insert


async def return_cartridge_from_departament(db: AsyncSession,
                                            positions: schemas.UpdateDepartmentCartridge):
    """Реализация возврата картриджа на заправку"""

    # TODO понизить счетчик в CounterCartidge
    # TODO повысить счетчик в StoreHouse
    sc = convert_from_depart_to_store(positions, unused=False, operation='+')
    await crud.upsert_in_store_house(db, sc)
    for cart in positions.cartridges:
        cart.amount = -cart.amount
    await crud.upsert_counter_cartridge(db, positions.cartridges)

async def replace_cartridge_departament(db: AsyncSession,
                                        cartridge: schemas.Cartridge):
    # TODO нужно реализовать замену картриджа на заправку
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
    await crud.upsert_counter_cartridge(db,
                                        counter_cartridge=store_house_list.cartridges)
    schema = convert_from_depart_to_store(schema=store_house_list,
                                          unused=True,
                                          operation='-')
    await crud.upsert_in_store_house(db, schema.cartridges)
    pass


async def shipment_of_cartridges(db: AsyncSession,
                                 store_house_list: schemas.UpdateStoreHouseBase):
    # отправка картриджей на заправку
    # Нужно обработать ошибку отсутствия сервисного отдела
    # up department_id==service and down unused==False
    service_depart = await crud.get_service_department(db)
    depart_cartridge = convert_from_store_to_depart(schema=store_house_list,
                                                    department_id=service_depart,
                                                    operation='+')
    await crud.upsert_counter_cartridge(db, depart_cartridge.cartridges)
    for item in store_house_list.cartridges:
        item.amount = -item.amount
    print(store_house_list.cartridges)
    await crud.upsert_in_store_house(db, store_house_list.cartridges)


async def receipt_of_cartridges(db: AsyncSession,
                                store_house_list: [schemas.StoreHouseBase]):
    await crud.upsert_in_store_house(db, store_house_list)


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
