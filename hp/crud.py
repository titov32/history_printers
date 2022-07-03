from sqlalchemy.orm import Session
from sqlalchemy import delete
from datetime import datetime

import models
import schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_cartridge(db: Session, cartridge_id: int):
    return db.query(models.Cartridge).filter(models.Cartridge.id == cartridge_id).first()


def get_printer_by_model(db: Session, model: str):
    return db.query(models.ModelPrinter).filter(models.ModelPrinter.model == model).first()


def get_model_printer_by_id(db: Session, id: int):
    return db.query(models.ModelPrinter).filter(models.ModelPrinter.id == id).first()


def create_model(db: Session, printer: schemas.ModelPrinterCreate):
    db_printer = models.ModelPrinter(brand = printer.brand,
                                     model = printer.model,
                                     type_p = printer.type_p.value,
                                     format_paper = printer.format_paper.value)
    db.add(db_printer)
    db.commit()
    db.refresh(db_printer)
    return db_printer


def create_printer(db: Session, printer: schemas.Printer):
    db_printer = models.Printer(**printer.dict())
    db.add(db_printer)
    db.commit()
    db.refresh(db_printer)
    return db_printer


def get_printer_by_sn(db: Session, sn: str):
    return db.query(models.Printer).filter(models.Printer.sn == sn).first()


def get_printer_not_work(db: Session):
    return db.query(models.Printer).filter(models.Printer.is_work == False).all()


def get_printer_by_id(db: Session, id: int):
    return db.query(models.Printer).filter(models.Printer.id == id).first()


def get_printer_by_id_with_history(db: Session, id: int):
    # return db.query(models.Printer).filter(models.Printer.id == id).\
    # join(models.History).filter(models.History.printer_id == id)

    q:db.query= db.query(models.Printer, models.History).filter(models.Printer.id==id)\
        .join(models.History, isouter=True).order_by(models.History.date.desc()).all()


    return q


def update_printer(db: Session, printer: schemas.Printer):
    db.query(models.Printer).filter(models.Printer.id == printer.id). \
        update(printer.dict(), synchronize_session="fetch")

    db.commit()
    return printer.dict()


def delete_printer(db: Session, printer_id):
    # это стиль 2.0х
    # printer_delete = delete(models.Printer).where(models.Printer.id == printer_id).\
    #     execution_options(synchronize_session="fetch")
    # db.execute(printer_delete)

    db.query(models.Printer).filter(models.Printer.id == printer_id).delete(synchronize_session="fetch")
    db.commit()
    return {"delete printer_id": printer_id}


def create_history_printer(user_id, history: schemas.HistoryBase,db: Session):
    db_history = models.History(**history.dict(), author_id=user_id,
                                date=datetime.now())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_history_by_printer_id(db: Session, printer_id: int):
    return db.query(models.History).filter(models.History.printer_id == printer_id).all()

