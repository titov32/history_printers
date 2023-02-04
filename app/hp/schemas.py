from typing import Optional, List
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


class DepartmentBase(BaseModel):
    name: str
    company: str
    service: bool=False


class Departament(DepartmentBase):
    id: int

    class Config:
        orm_mode = True


class CartridgeBase(BaseModel):
    number: str
    reused: bool


class Cartridge(CartridgeBase):
    id: int

    class Config:
        orm_mode = True


class CounterCartridgeBase(BaseModel):
    id_cartridge: int
    department_id: int
    amount: int


class CounterCartridge(CounterCartridgeBase):
    id: int

    class Config:
        orm_mode = True


class StoreHouseBase(BaseModel):
    id_cartridge: int
    amount: int
    unused: bool


class UpdateDepartmentCartridge(BaseModel):
    operation: str
    cartridges: List[CounterCartridgeBase]


class UpdateStoreHouseBase(BaseModel):
    operation: str
    cartridges: List[StoreHouseBase]


class StoreHouse(StoreHouseBase):
    id: int

    class Config:
        orm_mode = True


class JournalInnerConsumeBase(BaseModel):
    id_cartridge: int
    departament: int
    amount: int
    name: int
    unique_id_operation: int


class JournalInnerConsume(JournalInnerConsumeBase):
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


class PrinterConditionEnum(Enum):
    is_work = 'work'
    in_repair = 'repair'
    is_reserve = 'reserve'
    require_repair = 'require_repair'


class ConnectionEnum(Enum):
    ip: str = 'ip'
    usb: str = 'USB'


class PrinterBase(BaseModel):
    model_id: int
    department_id: int
    connection: ConnectionEnum = ConnectionEnum.usb
    ip: Optional[IPv4Interface]
    sn: str
    condition: PrinterConditionEnum = PrinterConditionEnum.is_work
    location: Optional[str] = None


class Printer(PrinterBase):
    id: int
    qr: str

    class Config:
        orm_mode = True


class PrinterCreate(PrinterBase):
    pass


class PrinterUpdate(BaseModel):
    description: Optional[str] = None
    printer: PrinterCreate

class HistoryBase(BaseModel):
    printer_id: int
    description: str
    path_file: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class History(HistoryBase):
    id: int

    class Config:
        orm_mode = True
