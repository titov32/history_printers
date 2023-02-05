from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy import orm
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.future import select
from .db import Base


association_cartridge = sa.Table(
    'association_cartridge',
    Base.metadata,
    sa.Column('model_printer_id', sa.ForeignKey('model_printer.id')),
    sa.Column('cartridge_id', sa.ForeignKey('cartridge.id')),
    __table_args__=(sa.UniqueConstraint('model_printer_id', 'cartridge_id',
                                        name='_model_printer_cartridge'),)
)


class Department(Base):
    __tablename__ = 'department'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    company = sa.Column(sa.String, nullable=False)
    service = sa.Column(sa.Boolean, default=False)
    printers = orm.relationship("Printer", back_populates='department')
    cartridge_counters = orm.relationship("CounterCartridge",
                                          back_populates='department')
    journal_accounting_cartridges = orm.relationship("JournalAccountingCartridges",
                                                     back_populates='department')

    def __repr__(self):
        return f'{self.name} {self.company}'


class Cartridge(Base):
    __tablename__ = 'cartridge'
    id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.String, nullable=False, unique=True)
    reused = sa.Column(sa.Boolean, default=True)
    model_printers = orm.relationship('ModelPrinter',
                                      secondary=association_cartridge,
                                      back_populates='cartridges')
    counter_cartridges = orm.relationship("CounterCartridge",
                                          back_populates='cartridge')


class CounterCartridge(Base):
    __tablename__ = 'counter_cartridge'
    id = sa.Column(sa.Integer, primary_key=True)
    id_cartridge = sa.Column(sa.Integer,
                             sa.ForeignKey('cartridge.id'))
    cartridge = orm.relationship('Cartridge',
                                 back_populates='counter_cartridges')
    department_id = sa.Column(sa.Integer, sa.ForeignKey('department.id'))
    department = orm.relationship(Department,
                                  back_populates='cartridge_counters')
    amount = sa.Column(sa.Integer)
    __table_args__ = (sa.UniqueConstraint('id_cartridge', 'department_id',
                                          name='_cartridge_department'),)


class JournalAccountingCartridges(Base):
    __tablename__ = 'journal_accounting_cartridges'
    id = sa.Column(sa.Integer, primary_key=True)
    id_cartridge = sa.Column(sa.Integer,
                             sa.ForeignKey('cartridge.id'))
    time_operation = sa.Column(sa.DateTime)
    department_id = sa.Column(sa.Integer, sa.ForeignKey('department.id'))
    department = orm.relationship(Department,
                                  back_populates='journal_accounting_cartridges')
    amount = sa.Column(sa.Integer)
    created_by = sa.Column(UUID(as_uuid=True), sa.ForeignKey('user.id'))
    notice = sa.Column(sa.String)
    unique_id_operation = sa.Column(sa.Integer)


class StoreHouse(Base):
    __tablename__ = 'storehouse'
    id = sa.Column(sa.Integer, primary_key=True)
    id_cartridge = sa.Column(sa.Integer,
                             sa.ForeignKey('cartridge.id'))
    unused = sa.Column(sa.Boolean)
    amount = sa.Column(sa.Integer)
    __table_args__ = (sa.UniqueConstraint('id_cartridge', 'unused',
                                          name='_cartridge_unused'),)


class ModelPrinter(Base):
    __tablename__ = "model_printer"
    id = sa.Column(sa.Integer, primary_key=True)
    brand = sa.Column(sa.String, nullable=False)
    model = sa.Column(sa.String, nullable=False)
    type_p = sa.Column(sa.String)
    format_paper = sa.Column(sa.String)
    printers = orm.relationship("Printer", back_populates='model_printer')
    cartridges = orm.relationship('Cartridge',
                                  secondary=association_cartridge,
                                  back_populates='model_printers')
    __table_args__ = (sa.UniqueConstraint('brand', 'model',
                                          name='_brand_model'),)

    def __repr__(self):
        return f'ModelPrinter={self.model}, brand="{self.brand}"'


class Printer(Base):
    __tablename__ = 'printer'
    id = sa.Column(sa.Integer, primary_key=True)
    model_id = sa.Column(sa.Integer,
                         sa.ForeignKey('model_printer.id'),
                         index=True)
    model_printer = orm.relationship('ModelPrinter', back_populates='printers')
    department_id = sa.Column(sa.Integer,
                              sa.ForeignKey('department.id'))
    department = orm.relationship(Department,
                                  back_populates='printers',
                                  lazy="joined")
    connection = sa.Column(sa.String, default='USB')
    ip = sa.Column(sa.String, default=None)
    sn = sa.Column(sa.String, unique=True, index=True)
    condition = sa.Column(sa.String)
    qr = sa.Column(sa.String)
    location = sa.Column(sa.String)
    histories = orm.relationship('History',
                                 back_populates='printer',
                                 cascade="all, delete",
                                 passive_deletes=True, )

    def __repr__(self):
        return f'Printer id={self.id}, sn={self.sn}'


class History(Base):
    __tablename__ = 'history'
    id = sa.Column(sa.Integer, primary_key=True)
    printer_id = sa.Column(sa.Integer,
                           sa.ForeignKey('printer.id', ondelete="CASCADE"),
                           index=True)
    printer = orm.relationship('Printer', back_populates='histories')
    date = sa.Column(sa.DateTime)
    description = sa.Column(sa.Text)
    path_file = sa.Column(sa.String)
    latitude = sa.Column(sa.String)
    longitude = sa.Column(sa.String)
    author_id = sa.Column(UUID(as_uuid=True),
                          sa.ForeignKey('user.id'),
                          index=True)
    author = orm.relationship('User', back_populates="histories")

    def __repr__(self):
        return f'history id {self.id}, desc: {self.description}'
