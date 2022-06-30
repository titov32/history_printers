from typing import List, Union
from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True


class Cartridge(BaseModel):
    id: int
    number: str
    # model_printers: int
    departament: Union[str, None] = None

    class Config:
        orm_mode = True


class ModelPrinterBase(BaseModel):
    brand: str
    model: str
    type_p: str


class ModelPrinterCreate(ModelPrinterBase):
    pass


class ModelPrinter(ModelPrinterBase):
    id: int

    class Config:
        orm_mode = True


class PrinterBase(BaseModel):
    model_id: int
    departament: str
    ip: Union[str, None] = None
    sn: str
    is_work: bool
    is_free: bool



class Printer(PrinterBase):
    id: int

    class Config:
        orm_mode = True

class PrinterCreate(PrinterBase):
    pass