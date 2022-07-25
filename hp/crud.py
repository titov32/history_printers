from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from sqlalchemy.orm.strategy_options import joinedload

from hp import models
from hp import schemas
from qr.utils import make_qr_code_by_path


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
    # TODO Убрать items
    return users_all


async def get_cartridge(db: AsyncSession, cartridge_id: int):
    statement = select(models.Cartridge)\
                .where(models.Cartridge.id == cartridge_id)
    cartridges = await db.execute(statement)
    return cartridges.all()


async def get_printer_by_model(db: AsyncSession, model: str):
    statement = select(models.ModelPrinter)\
                .where(models.ModelPrinter.model == model)
    return (await db.execute(statement)).first()


async def get_model_printer_by_id(db: AsyncSession, id_: int):
    statement = select(models.ModelPrinter)\
                .where(models.ModelPrinter.id == id_)
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


async def update_model_printer(db: AsyncSession, printer: schemas.ModelPrinter):
    db_printer = models.ModelPrinter(brand=printer.brand,
                                     id=printer.id,
                                     model=printer.model,
                                     type_p=printer.type_p.value,
                                     format_paper=printer.format_paper.value)
    await db.merge(db_printer)
    await db.commit()
    return db_printer


async def read_model_printers(db: AsyncSession):
    statement = select(models.ModelPrinter)
    response = await db.execute(statement)
    return response.scalars().all()


async def delete_model_printer(db: AsyncSession, id_: int):
    statement = delete(models.ModelPrinter)\
                .where(models.ModelPrinter.id == id_)
    await db.execute(statement)
    await db.commit()
    return {"delete model_printer_id": id_}


async def create_printer(db: AsyncSession, printer: schemas.PrinterCreate):
    printer.ip = printer.ip.ip.exploded
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    try:
        await db.commit()
    except Exception as e:
        print(f'Error!!! {e}')
        await db.rollback()
        raise
    await db.refresh(db_printer)
    # создание qr-code и запись в БД
    path_to_printer_in_qr = f'/printer/{db_printer.id}'
    name = f'Printer_id_{db_printer.id}'
    db_printer.qr = make_qr_code_by_path(path_to_printer_in_qr, name)
    await db.commit()
    await db.refresh(db_printer)
    return db_printer


async def get_printer_by_sn(db: AsyncSession, sn: str):
    statement = select(models.Printer).where(models.Printer.sn == sn)
    gotten_printer = await db.execute(statement)
    return gotten_printer.first()


async def get_printers_by_model_id(db: AsyncSession, model_id: int):
    statement = select(models.Printer, models.ModelPrinter) \
                .join(models.ModelPrinter) \
                .where(models.Printer.model_id == model_id)
    gotten_printers = await db.execute(statement)
    return gotten_printers.all()


async def get_all_printers(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
                .join(models.ModelPrinter)
    gotten_printer = await db.execute(statement)
    return gotten_printer.all()


async def get_report_printer_not_work(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.is_work == False)
    report = await db.execute(statement)
    return report.all()


async def get_report_printer_in_repair(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.repairing == True)
    report = await db.execute(statement)
    return report.all()


async def get_report_printer_free(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.is_free == False)
    report = await db.execute(statement)
    return report.all()


async def get_printer_by_id(db: AsyncSession, id: int):
    statement = select(models.Printer).where(models.Printer.id == id)
    response = await db.execute(statement)
    return response.first()


async def get_printer_by_id_with_history(db: AsyncSession, id: int):
    statement = select(models.History,
                       models.User) \
        .where(models.History.printer_id == id) \
        .join(models.Printer) \
        .join(models.User) \
        .order_by(models.History.date.desc())
    printers = await db.execute(statement)
    statement = select(models.ModelPrinter, models.Printer) \
                .where(models.Printer.id==id) \
                .join(models.Printer)
    models_printer = await db.execute(statement)
    return models_printer.all() + printers.all()


async def update_printer(db: AsyncSession, printer: schemas.Printer):
    statement = update(models.Printer) \
        .where(models.Printer.id == printer.id) \
        .values(printer.dict())
    await db.execute(statement)
    await db.commit()
    return printer.dict()


async def delete_printer(db: AsyncSession, printer_id):
    printer_delete = delete(models.Printer).where(models.Printer.id == printer_id). \
        execution_options(synchronize_session="fetch")
    await db.execute(printer_delete)
    await db.commit()
    return {"delete printer_id": printer_id}


async def create_history_printer( db: AsyncSession, user_id, history: schemas.HistoryBase):
    db_history = models.History(**history.dict(), author_id=user_id,
                                date=datetime.now())
    db.add(db_history)
    await db.commit()
    await db.refresh(db_history)
    return db_history


async def update_printer_with_history(db: AsyncSession,
                                      printer: schemas.PrinterUpdate,
                                      description: schemas.HistoryBase,
                                      user_id):
    printer.ip = printer.ip.ip.exploded
    db_history = models.History(**description.dict(), author_id=user_id,
                                date=datetime.now())

    statement = update(models.Printer) \
        .where(models.Printer.id == printer.id) \
        .values(printer.dict())
    await db.execute(statement)
    db.add(db_history)
    await db.commit()
    await db.refresh(db_history)

    return printer
