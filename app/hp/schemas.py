from typing import List, Union, Optional
from pydantic import BaseModel
from ipaddress import IPv4Interface
from enum import Enum


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class CartridgeBase(BaseModel):
    number: str
    model_printers: int


class Cartridge(CartridgeBase):
    id: int

    class Config:
        orm_mode = True


class TypeEnum(Enum):
    m = 'МФУ'
    p = 'Принтер'


class FormatEnum(Enum):
    A0 = 'A0'
    A1 = 'A1'
    A3 = 'A3'
    A4 = 'A4'


class ModelPrinterBase(BaseModel):
    brand: str
    model: str
    type_p: TypeEnum = TypeEnum.m
    format_paper: FormatEnum = FormatEnum.A4


class ModelPrinterCreate(ModelPrinterBase):
    pass


class ModelPrinter(ModelPrinterBase):
    id: int

    class Config:
        orm_mode = True


class PrinterBase(BaseModel):
    model_id: int
    departament: str
    ip: Optional[IPv4Interface] = None
    sn: str
    is_work: Optional[bool] = True
    is_free: Optional[bool] = False
    repairing: Optional[bool] = False
    location: Optional[str] = None

class Printer(PrinterBase):
    id: int
    qr: str

    class Config:
        orm_mode = True


class PrinterCreate(PrinterBase):
    pass


class PrinterUpdate(PrinterBase):
    id: int

class HistoryBase(BaseModel):
    printer_id: int
    description: str
    path_file: Optional[str] = None



class History(HistoryBase):
    id: int

    class Config:
        orm_mode = True