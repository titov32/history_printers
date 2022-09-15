from sqlalchemy.ext.asyncio import AsyncSession
from app.hp import schemas
from app.hp import crud

from . import models
from sqlalchemy.dialects.postgresql import insert

async def return_cartridge_from_departament(db: AsyncSession,
                                            cartridge: schemas.Cartridge):
    """Реализация возврата картриджа на заправку"""

    # TODO понизить счетчик в CounterCartidge
    # TODO повысить счетчик в StoreHouse


async def replace_cartridge_departament(db: AsyncSession,
                                        cartridge: schemas.Cartridge):
    # TODO нужно реализовать замену картриджа на заправку
    pass


async def put_cartridge_departament(db: AsyncSession,
                                    cartridge: schemas.Cartridge):
    # TODO нужно реализовать передачу картриджа на отделу без возврата
    pass


async def put_cartridge_departament_with_return(db: AsyncSession,
                                                cartridges: [schemas.CounterCartridgeBase]):
    # TODO нужно реализовать передачу картриджа отделу c возвратом
    # нужно повысить счетчик отдела и понизить счетчик на складе
    await crud.create_counter_cartridge(db, counter_cartridge=cartridges)
    pass


async def shipment_of_cartridges(db: AsyncSession,
                                 cartridge: schemas.Cartridge):
    # TODO нужно реализовать отправку картриджей на заправку
    pass


async def receipt_of_cartridges(db: AsyncSession,
                                store_house_list: [schemas.ListCartridges]):
    for record in store_house_list:
        stmt = insert(models.StoreHouse).values(id_cartridge=record.id_cartridge,
                                                amount=record.amount,
                                                unused=record.unused)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.StoreHouse.id_cartridge, models.StoreHouse.unused],
            set_=dict(amount=stmt.excluded.amount+models.StoreHouse.amount)
        )
        await db.execute(stmt)
    return await db.commit()


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
