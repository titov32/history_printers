from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from datetime import datetime

from . import models
from app.auth import models as auth_models
from . import schemas
from .utils.qr import make_qr_code_by_path
from .utils.logger import log_api_route

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
    if printer.ip:
        printer.ip = printer.ip.ip.exploded
    printer.condition = printer.condition.value
    printer.connection = printer.connection.value
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    try:
        await db.commit()
    except Exception as e:
        log_api_route(f"Ошибка создания: {{e}}")
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
        .where(models.Printer.condition == 'require_repair')
    report = await db.execute(statement)
    return report.all()


async def get_report_printer_in_repair(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.condition == 'repair')
    report = await db.execute(statement)
    return report.all()


async def get_report_printer_free(db: AsyncSession):
    statement = select(models.Printer, models.ModelPrinter) \
        .join(models.ModelPrinter) \
        .where(models.Printer.condition == 'reserve')
    report = await db.execute(statement)
    return report.all()


async def get_printer_by_id(db: AsyncSession, id_: int):
    statement = select(models.Printer, models.Department).join(
        models.Department).where(models.Printer.id == id_)
    response = await db.execute(statement)
    return response.first()


async def get_printer_by_id_with_history(db: AsyncSession, id_: int):
    statement = select(models.History,
                       auth_models.User) \
        .where(models.History.printer_id == id_) \
        .join(models.Printer) \
        .join(auth_models.User) \
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
                                      printer: schemas.PrinterBase,
                                      printer_id: int,
                                      description: schemas.HistoryBase,
                                      user_id, ):
    if printer.ip:
        printer.ip = printer.ip.ip.exploded
    printer.condition = printer.condition.value
    printer.connection = printer.connection.value
    db_history = models.History(**description.dict(), author_id=user_id,
                                date=datetime.now())

    statement = update(models.Printer) \
        .where(models.Printer.id == printer_id) \
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
    return cartridges.scalars().first()


async def get_all_id_reused_cartridges(db: AsyncSession, list_id: list):
    stmt = select(models.Cartridge.id) \
        .where(models.Cartridge.reused == True) \
        .where(models.Cartridge.id.in_(list_id))
    print(stmt)
    id_cartridges = await db.execute(stmt)
    return id_cartridges.scalars().all()


async def get_cartridges(db: AsyncSession):
    statement = select(models.Cartridge)
    cartridges = await db.execute(statement)
    return cartridges.scalars().all()


async def get_cartridges_unlinked(db: AsyncSession, model_id):
    statement = select(models.Cartridge) \
        .except_all(select(models.Cartridge)
                    .select_from(models.association_cartridge) \
                    .join(models.Cartridge,
                          models.association_cartridge.c.cartridge_id == models.Cartridge.id) \
                    .where(
        models.association_cartridge.c.model_printer_id == model_id))
    print(statement)
    r = await db.execute(statement)
    return r.all()


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
    # обновление картриджа
    statement = update(models.Cartridge) \
        .where(models.Cartridge.id == cartridge.id) \
        .values(cartridge.dict())
    await db.execute(statement)
    await db.commit()
    return cartridge.dict()


async def delete_cartridge(db: AsyncSession, cartridge_id: int):
    # TODO нужно обработать ошибку удаления картриджа находящихся на складе(в другой таблице)
    cartridge_delete = delete(models.Cartridge).where(
        models.Cartridge.id == cartridge_id). \
        execution_options(synchronize_session="fetch")
    await db.execute(cartridge_delete)
    await db.commit()
    return {"delete cartridge_id": cartridge_id}


def upsert_counter_cartridge(counter_cartridge: [
    schemas.CounterCartridgeBase]):
    # реализация создания записи картриджа в отделе
    records = []
    for record in counter_cartridge:
        stmt = insert(models.CounterCartridge) \
            .values(id_cartridge=record.id_cartridge,
                    amount=record.amount,
                    department_id=record.department_id)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.CounterCartridge.id_cartridge,
                            models.CounterCartridge.department_id],
            set_=dict(
                amount=stmt.excluded.amount + models.CounterCartridge.amount)
        )
        records.append(stmt)
    return records


def upsert_in_store_house(store_house_list: [schemas.StoreHouseBase]):
    # реализация создания записи картриджа на складе
    records = []
    for record in store_house_list:
        stmt = insert(models.StoreHouse).values(
            id_cartridge=record.id_cartridge,
            amount=record.amount,
            unused=record.unused)
        stmt = stmt.on_conflict_do_update(
            index_elements=[models.StoreHouse.id_cartridge,
                            models.StoreHouse.unused],
            set_=dict(amount=stmt.excluded.amount + models.StoreHouse.amount)
        )
        records.append(stmt)

    return records


async def get_cartridge_in_store_house_by_cartridge_unused(db: AsyncSession,
                                                           id_: int,
                                                           unused: bool):
    statement = select(models.StoreHouse). \
        where(
        models.StoreHouse.id_cartridge == id_ and models.StoreHouse.unused == unused)
    response = await db.execute(statement)
    return response.first()


async def get_all_cartridges_in_store_house(db: AsyncSession, unused):
    statement = select(models.StoreHouse, models.Cartridge.number) \
        .join(models.Cartridge) \
        .where(models.StoreHouse.unused == unused) \
        .order_by(models.Cartridge.number)
    response = await db.execute(statement)
    return response.all()


async def get_all_cartridges_in_departments(db: AsyncSession):
    statement = select(models.CounterCartridge,
                       models.Cartridge.number,
                       models.Department) \
        .join(models.Cartridge) \
        .join(models.Department) \
        .order_by(models.CounterCartridge.department_id)
    response = await db.execute(statement)
    return response.all()


async def get_counter_by_cart_id_and_depart(db: AsyncSession, id_: int,
                                            depart: int):
    statement = select(models.CounterCartridge). \
        where(
        models.CounterCartridge.id_cartridge == id_ and
        models.CounterCartridge.departament == depart)
    response = await db.execute(statement)
    return response.first()


async def upsert_cart_for_model(db: AsyncSession, model: int, cart: int):
    # реализация создания записи картриджа на складе
    stmt = insert(models.association_cartridge).values(
        model_printer_id=model,
        cartridge_id=cart)
    stmt = stmt.on_conflict_do_nothing()
    await db.execute(stmt)
    return await db.commit()


async def delete_cart_for_model(db: AsyncSession, model: int, cart: int):
    delete_stmt = delete(models.association_cartridge) \
        .where(models.association_cartridge.c.model_printer_id == model,
               models.association_cartridge.c.cartridge_id == cart) \
        .execution_options(synchronize_session="fetch")
    await db.execute(delete_stmt)
    await db.commit()


async def get_departments(db: AsyncSession):
    statement = select(models.Department) \
        .where(models.Department.service == False)
    departments = await db.execute(statement)
    return departments.scalars().all()


async def get_department_by_id(db: AsyncSession, id_: int):
    statement = select(models.Department).where(models.Department.id == id_)
    departments = await db.execute(statement)
    return departments.scalars().first()


async def get_service_department(db: AsyncSession):
    statement = select(models.Department.id) \
        .where(models.Department.service == True)
    departments = await db.execute(statement)
    return departments.scalars().first()


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


async def get_list_depart_use_cart(db: AsyncSession, id_cart: int):
    stmt = text("""
    SELECT department.name, count(*)
    FROM model_printer
    JOIN association_cartridge ON model_printer.id = association_cartridge.model_printer_id
    JOIN cartridge ON association_cartridge.cartridge_id = cartridge.id
    JOIN printer ON printer.model_id = model_printer.id
    JOIN department ON department.id = printer.department_id
    WHERE cartridge.id = :id_cart
    GROUP BY department.name
    """)
    departments = await db.execute(stmt, {'id_cart': id_cart})
    return departments.all()


async def get_sum_all_by_id_cart(db: AsyncSession, id_cart: int):
    stmt = text("""
-- общая сумма картриджей
    SELECT SUM(amount)
    FROM (
    SELECT number, amount
    FROM storehouse
    JOIN cartridge ON storehouse.id_cartridge=cartridge.id
    WHERE cartridge.id = :id_cart
    UNION ALL
    
    SELECT number, amount
    FROM counter_cartridge
    JOIN cartridge ON counter_cartridge.id_cartridge=cartridge.id
    JOIN department ON counter_cartridge.department_id=department.id
    WHERE cartridge.id = :id_cart) a;
    """)
    departments = await db.execute(stmt, {'id_cart': id_cart})
    return departments.scalars().first()


async def get_sum_all_by_id_cart_in_storehouse(db: AsyncSession, id_cart: int):
    stmt = select(func.sum(models.StoreHouse.amount)) \
        .where(models.StoreHouse.id_cartridge == int(id_cart))

    cart = await db.execute(stmt)
    return cart.scalars().first()


async def get_all_by_id_cart_in_departs(db: AsyncSession, id_cart: int):
    stmt = select(models.CounterCartridge) \
        .join(models.Department) \
        .where(models.CounterCartridge.id_cartridge == int(id_cart)) \
        .where(models.Department.service == False)

    cart = await db.execute(stmt)
    return cart.scalars().all()


async def get_used_cart(db: AsyncSession, id_cart: int):
    stmt = select(models.CounterCartridge) \
        .join(models.Department) \
        .where(models.CounterCartridge.id_cartridge == int(id_cart)) \
        .where(models.Department.service == True)

    cart = await db.execute(stmt)
    return cart.scalars().all()
