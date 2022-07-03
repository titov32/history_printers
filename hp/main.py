from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
from db import SessionLocal, engine
from fastapi.staticfiles import StaticFiles
from qr.utils import make_qr_code_by_path
from config import DOMAIN_NAME


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def get_test():
    return {'test':'ok'}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already is registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User is not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int,
                         item: schemas.ItemCreate,
                         db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get("/cartridge/{cartridge_id}") #, response_model=schemas.Cartridge
def read_cartridge(cartridge_id: int, db: Session = Depends(get_db)):
    db_cartridge = crud.get_cartridge(db, cartridge_id)
    if db_cartridge is None:
        raise HTTPException(status_code=404, detail="Cartridge is not found")
    return db_cartridge


@app.post("/model_printer/", response_model=schemas.ModelPrinter)
def create_model_printer(printer: schemas.ModelPrinterCreate, db: Session = Depends(get_db)):
    db_model = crud.get_printer_by_model(db, model=printer.model)
    if db_model:
        raise HTTPException(status_code=400, detail="Model already registered")
    return crud.create_model(db=db, printer=printer)


@app.post("/printer/", response_model=schemas.Printer)
def create_printer(printer: schemas.PrinterCreate, db: Session = Depends(get_db)):
    db_printer = crud.get_printer_by_sn(db, printer.sn)
    if db_printer:
        raise HTTPException(status_code=400, detail="Printer already registered")
    printer_id = crud.get_model_printer_by_id(db, id = printer.model_id)
    if not printer_id:
        raise HTTPException(status_code=400, detail='Model printer is not exist')


    created_printer =  crud.create_printer(db=db, printer=printer)
    path = f'/printer/{created_printer.id}'
    name = f'Printer_id_{created_printer.id}'
    make_qr_code_by_path(path, name)
    return created_printer

@app.get("/printer/not_work")
def get_not_work_printer(db: Session = Depends(get_db)):
    printers = crud.get_printer_not_work(db)
    return printers


@app.put("/printer/", response_model=schemas.Printer)
def update_printer(printer: schemas.Printer,
                   db: Session = Depends(get_db)):
    db_printer = crud.get_printer_by_id(db, printer.id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    return crud.update_printer(db, printer)


@app.delete("/printer/")
def delete_printer(printer: schemas.Printer, db: Session = Depends(get_db)):
    return crud.delete_printer(db, printer.id)

@app.get("/printer/{printer_id}")
def read_printer(printer_id: int, db: Session = Depends(get_db)):
    """
    авававава
    :param printer_id:
    :param db:
    :return:
    """
    db_printer = crud.get_printer_by_id_with_history(db, printer_id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    # db_printer.__dict__['qr']=f'http://{DOMAIN_NAME}/static/Printer_id_{db_printer.id}.png'
    return db_printer


@app.post("/{user_id}/history")
def create_history_printer(user_id:int, history: schemas.HistoryBase,
                           db: Session = Depends(get_db)):
    return crud.create_history_printer(user_id, history, db)
