from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from datetime import datetime

from hp import models
from hp import schemas


async def get_user(db: AsyncSession, user_id: int):
    query = select(models.User).where(models.User.id == user_id)
    users = await db.execute(query)
    user = users.first()[0]

    return user


async def get_user_by_email(db: AsyncSession, email: str):
    statement = select(models.User).where(models.User.email == email)
    return (await db.execute(statement)).all()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query: select = select(models.User, models.Item) \
        .join(models.Item.owner) \
        .where(models.User.id >= skip).limit(limit)
    users = await db.execute(query)
    users_all = users.all()
    return users_all


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    return user


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    statement = select(models.Item).where(models.Item.id > skip).limit(limit)
    items = (await db.execute(statement)).all()
    return items


async def create_user_item(db: AsyncSession, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def get_cartridge(db: AsyncSession, cartridge_id: int):
    statement = select(models.Cartridge).where(models.Cartridge.id == cartridge_id)
    cartridges = await db.execute(statement)
    return cartridges.all()


async def get_printer_by_model(db: AsyncSession, model: str):
    statement = select(models.ModelPrinter).where(models.ModelPrinter.model == model)
    return (await db.execute(statement)).first()


async def get_model_printer_by_id(db: AsyncSession, id_: int):
    statement = select(models.ModelPrinter).where(models.ModelPrinter.id == id_)
    return (await db.execute(statement)).first()


async def create_model(db: AsyncSession, printer: schemas.ModelPrinterCreate):
    db_printer = models.ModelPrinter(brand=printer.brand,
                                     model=printer.model,
                                     type_p=printer.type_p.value,
                                     format_paper=printer.format_paper.value)
    db.add(db_printer)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    await db.refresh(db_printer)
    return db_printer


async def create_printer(db: AsyncSession, printer: schemas.Printer):
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    try:
        await db.commit()
    except Exception as e:
        print(f'Error!!! {e}')
        await db.rollback()
        raise
    await db.refresh(db_printer)
    return db_printer


async def get_printer_by_sn(db: AsyncSession, sn: str):
    statement = select(models.Printer).where(models.Printer.sn == sn)
    gotten_printer = await db.execute(statement)
    return gotten_printer.first()


async def get_printer_not_work(db: AsyncSession):
    statement = select(models.Printer).where(models.Printer.is_work == False)
    report = await db.execute(statement)
    return report.all()


async def get_printer_by_id(db: AsyncSession, id: int):
    statement = select(models.Printer).where(models.Printer.id == id)
    response = await db.execute(statement)
    return response.first()


async def get_printer_by_id_with_history(db: AsyncSession, id: int):
    statement = select(models.Printer, models.History) \
        .where(models.Printer.id == id) \
        .join(models.History, isouter=True) \
        .order_by(models.History.date.desc())
    printers = await db.execute(statement)
    return printers.all()


async def update_printer(db: AsyncSession, printer: schemas.Printer):
    # update(models.Printer).where(models.Printer.id == printer.id). \
    #     update(printer.dict(), synchronize_session="fetch")
    statement = update(models.Printer) \
        .where(models.Printer.id == printer.id) \
        .values(printer.dict())
    await db.execute(statement)
    await db.commit()
    return printer.dict()


async def delete_printer(db: AsyncSession, printer_id):
    # это стиль 2.0х
    printer_delete = delete(models.Printer).where(models.Printer.id == printer_id). \
        execution_options(synchronize_session="fetch")
    await db.execute(printer_delete)
    await db.commit()
    # это стиль 1.0, с async не работает
    # db.query(models.Printer).filter(models.Printer.id == printer_id).delete(synchronize_session="fetch")
    # db.commit()
    return {"delete printer_id": printer_id}


async def create_history_printer(user_id, history: schemas.HistoryBase, db: AsyncSession):
    db_history = models.History(**history.dict(), author_id=user_id,
                                date=datetime.now())
    db.add(db_history)
    await db.commit()
    await db.refresh(db_history)
    return db_history
