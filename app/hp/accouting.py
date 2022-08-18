from sqlalchemy.ext.asyncio import AsyncSession
from app.hp import schemas
from app.hp import crud


async def return_cartridge_from_departament(db: AsyncSession,
                                            cartridge: schemas.Cartridge):
    """Реализация возврата картриджа на заправку"""

    #TODO Нужно отобразить транзакцию в журнале,
    # TODO понизить счетчик в CounterCartidge
    #  TODO повысить счетчик в StoreHouse


async def replace_cartridge_departament(db: AsyncSession,
                                        cartridge: schemas.Cartridge):
    # TODO нужно реализовать замену картриджа на заправку
    pass


async def put_cartridge_departament(db: AsyncSession,
                                    cartridge: schemas.Cartridge):
    # TODO нужно реализовать передачу картриджа на отделу без возврата
    pass


async def put_cartridge_departament_with_return(db: AsyncSession,
                                                cartridge: schemas.Cartridge):
    # TODO нужно реализовать передачу картриджа на отделу c возвратом
    pass


async def shipment_of_cartridges(db: AsyncSession,
                                    cartridge: schemas.Cartridge):
    # TODO нужно реализовать отправку картриджей на заправку
    pass


async def receipt_of_cartridges(db: AsyncSession,
                                        cartridges: [schemas.Cartridge]):
    # TODO нужно реализовать прием картриджей с заправки
    for cartridge in cartridges:
        check_value = await crud.get_cartridge_in_store_house_by_cartridge_unused(db=db, unused=True, id=cartridge.id)
        if check_value:
            await crud.update_cartridge_in_storehouse(db=db, cartridge=cartridge, unused=True)
        else:
            await crud.create_cartridge_in_store_house(db=db, counter_cartridge=cartridge)
    # TODO нужно повысить счетчики в StoreHouse
    # TODO нужно отобразить JournalInnerConsume

    pass


async def report_cartridgies_on_storehouse_unused(db: AsyncSession,
                                                  cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам
    pass


async def report_cartridgies_on_storehouse_used(db: AsyncSession,
                                                cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам требующих заправки
    pass


async def report_cartridges_with_model(db: AsyncSession,
                                       cartridge: schemas.Cartridge):
    # TODO нужно реализовать отчет по картриджам по моделям принтеров
    pass