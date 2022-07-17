from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import crud
import schemas
from db import get_db
from fastapi.staticfiles import StaticFiles
from qr.utils import make_qr_code_by_path


# models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def get_test():
    return {'test':'ok'}


@app.post("/users/")#, response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already is registered")
    return await crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    dict_users={}
    for user, items in users:
        if not dict_users.get(user.id):
            dict_users[user.id]={'id':user.id, 'is_active':user.is_active, 'email':user.email, 'items':[]}
            dict_users[user.id]['items'].append(items)
        else:
            dict_users[user.id]['items'].append(items)
    return list(dict_users.values())


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User is not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
async def create_item_for_user(user_id: int,
                         item: schemas.ItemCreate,
                         db: AsyncSession = Depends(get_db)):
    return await crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/")#, response_model=list[schemas.Item])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get("/cartridge/{cartridge_id}") #, response_model=schemas.Cartridge
async def read_cartridge(cartridge_id: int, db: AsyncSession = Depends(get_db)):
    db_cartridge = crud.get_cartridge(db, cartridge_id)
    if db_cartridge is None:
        raise HTTPException(status_code=404, detail="Cartridge is not found")
    return await db_cartridge


@app.post("/model_printer/", response_model=schemas.ModelPrinter)
async def create_model_printer(printer: schemas.ModelPrinterCreate, db: AsyncSession = Depends(get_db)):
    db_model = await crud.get_printer_by_model(db, model=printer.model)
    if db_model:
        raise HTTPException(status_code=400, detail="Model already registered")
    return await crud.create_model(db=db, printer=printer)


@app.post("/printer/")#, response_model=schemas.Printer)
async def create_printer(printer: schemas.PrinterCreate, db: AsyncSession = Depends(get_db)):
    db_printer = await crud.get_printer_by_sn(db, printer.sn)
    if db_printer:
        raise HTTPException(status_code=400, detail="Printer already registered")
    printer_id =await crud.get_model_printer_by_id(db, id_= printer.model_id)
    if not printer_id:
        raise HTTPException(status_code=400, detail='Model printer is not exist')

    created_printer = await crud.create_printer(db=db, printer=printer)
    path = f'/printer/{created_printer.id}'
    name = f'Printer_id_{created_printer.id}'
    make_qr_code_by_path(path, name)
    return created_printer


@app.get("/printer/not_work")
async def get_not_work_printer(db: AsyncSession = Depends(get_db)):
    printers = await crud.get_printer_not_work(db)
    return printers


@app.put("/printer/", response_model=schemas.Printer)
async def update_printer(printer: schemas.Printer,
                   db: AsyncSession = Depends(get_db)):
    db_printer = await crud.get_printer_by_id(db, printer.id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    return await crud.update_printer(db, printer)


@app.delete("/printer/")
async def delete_printer(printer: schemas.Printer, db: AsyncSession = Depends(get_db)):
    return await crud.delete_printer(db, printer.id)


@app.get("/printer/{printer_id}")
async def read_printer(printer_id: int, db: AsyncSession = Depends(get_db)):

    db_printer = await crud.get_printer_by_id_with_history(db, printer_id)
    if db_printer is None:
        raise HTTPException(status_code=404, detail="Printer is not found")
    # db_printer.__dict__['qr']=f'http://{DOMAIN_NAME}/static/Printer_id_{db_printer.id}.png'

    return db_printer


@app.post("/{user_id}/history")
async def create_history_printer(user_id:int,
                                 history: schemas.HistoryBase,
                                 db: AsyncSession = Depends(get_db)):
    return await crud.create_history_printer(user_id, history, db)
