from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from . import models
from . import schemas
from .utils.qr import make_qr_code_by_path


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email,
                          hashed_password=fake_hashed_password)
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
    query: select = select(models.User) \
        .where(models.User.id >= skip).limit(limit)
    users = await db.execute(query)
    users_all = users.all()
    return users_all


async def get_printer_by_model(db: AsyncSession, model: str):
    statement = select(models.ModelPrinter) \
        .where(models.ModelPrinter.model == model)
    return (await db.execute(statement)).first()


async def get_model_printer_by_id(db: AsyncSession, id_: int):
    statement = select(models.ModelPrinter) \
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


async def update_model_printer(db: AsyncSession,
                               printer: schemas.ModelPrinter):
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


async def read_model_with_cartridges(db: AsyncSession):
    st = select(models.ModelPrinter, models.Cartridge.number) \
        .join(models.association_cartridge,
              models.association_cartridge.c.model_printer_id == models.ModelPrinter.id,
              isouter=True) \
        .join(models.Cartridge,
              models.association_cartridge.c.cartridge_id == models.Cartridge.id,
              isouter=True)
    r = await db.execute(st)
    d = {}
    for i in r.all():
        d.setdefault(i[0], [])
        if i[1] not in d[i[0]]:
            d[i[0]].append(i[1])
    return d


async def delete_model_printer(db: AsyncSession, id_: int):
    statement = delete(models.ModelPrinter) \
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


async def get_printers_by_departament(db: AsyncSession, department: int):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.department_id == department)
    gotten_printers = await db.execute(statement)
    return gotten_printers.all()


async def get_all_printers(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter, models.Department) \
        .join(models.ModelPrinter) \
        .join(models.Department)
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
        .where(models.Printer.is_free == True)
    report = await db.execute(statement)
    return report.all()


async def get_printer_by_id(db: AsyncSession, id_: int):
    statement = select(models.Printer, models.Department).join(
        models.Department).where(models.Printer.id == id_)
    response = await db.execute(statement)
    return response.first()


async def get_printer_by_id_with_history(db: AsyncSession, id_: int):
    statement = select(models.History,
                       models.User) \
        .where(models.History.printer_id == id_) \
        .join(models.Printer) \
        .join(models.User) \
        .order_by(models.History.date.desc())
    printers = await db.execute(statement)
    statement = select(models.ModelPrinter, models.Printer) \
        .where(models.Printer.id == id_) \
        .join(models.Printer)
    models_printer = await db.execute(statement)
    return models_printer.all() + printers.all()


async def update_printer(db: AsyncSession, printer: schemas.Printer):
    printer.ip = printer.ip.ip.exploded
    statement = update(models.Printer) \
        .where(models.Printer.id == printer.id) \
        .values(printer.dict())
    await db.execute(statement)
    await db.commit()
    return printer.dict()


async def delete_printer(db: AsyncSession, printer_id):
    printer_delete = delete(models.Printer).where(
        models.Printer.id == printer_id). \
        execution_options(synchronize_session="fetch")
    await db.execute(printer_delete)
    await db.commit()
    return {"delete printer_id": printer_id}


async def create_history_printer(db: AsyncSession, user_id,
                                 history: schemas.HistoryBase):
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


async def get_cartridge_by_id(db: AsyncSession, cartridge_id: int):
    statement = select(models.Cartridge) \
        .where(models.Cartridge.id == cartridge_id)
    cartridges = await db.execute(statement)
    return cartridges.all()


async def get_cartridges(db: AsyncSession):
    statement = select(models.Cartridge)
    cartridges = await db.execute(statement)
    return cartridges.scalars().all()


async def get_cartridges_by_model_id(db: AsyncSession, model_id: int):
    st = select(models.Cartridge).select_from(models.association_cartridge) \
        .join(models.Cartridge,
              models.association_cartridge.c.cartridge_id == models.Cartridge.id) \
        .where(models.association_cartridge.c.model_printer_id == model_id)
    r = await db.execute(st)

    return r.scalars().all()


async def create_cartridge(db: AsyncSession, cartridge: schemas.CartridgeBase):
    """
    создание картриджа
    """
    db_cartridge = models.Cartridge(**cartridge.dict())
    db.add(db_cartridge)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    await db.refresh(db_cartridge)
    return db_cartridge


async def update_cartridge(db: AsyncSession, cartridge: schemas.Cartridge):
    # TODO нужно проверить обновление картриджа

    statement = update(models.Cartridge) \
        .where(models.Cartridge.id == cartridge.id) \
        .values(cartridge.dict())
    await db.execute(statement)
    await db.commit()
    return cartridge.dict()


async def delete_cartridge(db: AsyncSession, cartridge_id: int):
    # TODO нужно проверить удаление картриджа
    cartridge_delete = delete(models.Cartridge).where(
        models.Cartridge.id == cartridge_id). \
        execution_options(synchronize_session="fetch")
    await db.execute(cartridge_delete)
    await db.commit()
    return {"delete cartridge_id": cartridge_id}


async def create_counter_cartridge(db: AsyncSession,
                                   counter_cartridge: schemas.CounterCartridgeBase):
    # TODO нужно реалзиовать создание записи картриджа
    db_counter_cartridge = models.CounterCartridge(
        departament=counter_cartridge.departament,
        amount=counter_cartridge.amount)
    db.add(db_counter_cartridge)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    await db.refresh(db_counter_cartridge)
    return db_counter_cartridge


async def create_cartridge_in_store_house(db: AsyncSession,
                                          counter_cartridge: schemas.CounterCartridgeBase):
    # TODO нужно реалзиовать создание записи картриджа
    db_counter_cartridge = models.StoreHouse(**counter_cartridge.dict())
    db.add(db_counter_cartridge)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    await db.refresh(db_counter_cartridge)
    return db_counter_cartridge


async def get_cartridge_in_store_house_by_cartridge_unused(db: AsyncSession,
                                                           id_: int,
                                                           unused: bool):
    statement = select(models.StoreHouse). \
        where(
        models.StoreHouse.id_cartridge == id_ and models.StoreHouse.unused == unused)
    response = await db.execute(statement)
    return response.first()


async def get_all_cartridges_in_store_house(db: AsyncSession, used):
    statement = select(models.StoreHouse, models.Cartridge.number) \
        .join(models.Cartridge) \
        .where(models.StoreHouse.unused == used)
    response = await db.execute(statement)
    return response.all()


async def update_cartridge_in_storehouse(db: AsyncSession,
                                         cartridge: schemas.Cartridge,
                                         unused: bool):
    # TODO нужно проверить обновление картриджа

    statement = update(models.StoreHouse) \
        .where(models.StoreHouse.id_cartridge == cartridge.id and
               models.StoreHouse.unused == unused) \
        .values(cartridge.dict())
    await db.execute(statement)
    await db.commit()
    return cartridge.dict()


async def get_counter_by_cart_id_and_depart(db: AsyncSession, id_: int,
                                            depart: int):
    statement = select(models.CounterCartridge). \
        where(
        models.CounterCartridge.id_cartridge == id_ and
        models.CounterCartridge.departament == depart)
    response = await db.execute(statement)
    return response.first()


async def add_cart_for_model(db: AsyncSession, model: int, cart: int):
    # TODO нужно переделать в upsert, нужно избавится от дублей при
    #  добавление картриджей
    ins = models.association_cartridge.insert().values(model_printer_id=model,
                                                       cartridge_id=cart)
    await db.execute(ins)
    await db.commit()


async def delete_cart_for_model(db: AsyncSession, model: int, cart: int):
    delete_stmt = delete(models.association_cartridge) \
        .where(models.association_cartridge.c.model_printer_id == model,
               models.association_cartridge.c.cartridge_id == cart) \
        .execution_options(synchronize_session="fetch")
    await db.execute(delete_stmt)
    await db.commit()


async def get_departments(db: AsyncSession):
    statement = select(models.Department)
    departments = await db.execute(statement)
    return departments.scalars().all()


async def get_department_by_id(db: AsyncSession, id_: int):
    statement = select(models.Department).where(models.Department.id == id_)
    departments = await db.execute(statement)
    return departments.first()


async def create_department(db: AsyncSession,
                            department: schemas.DepartmentBase):
    db_department = models.Department(**department.dict())
    db.add(db_department)
    try:
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    await db.refresh(db_department)
    return db_department
