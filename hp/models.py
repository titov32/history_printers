from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy import orm
import sqlalchemy as sa
from hp.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    histories = orm.relationship("History", back_populates="author")

    def __repr__(self):
        return f'UserID {self.id} UserEmail {self.email}'


association_cartridge = sa.Table(
    'association_cartridge',
    Base.metadata,
    sa.Column('model_printer_id', sa.ForeignKey('model_printer.id')),
    sa.Column('cartridge_id', sa.ForeignKey('cartridge.id'))
)


class Cartridge(Base):
    __tablename__ = 'cartridge'
    id = sa.Column(sa.Integer, primary_key=True)
    number = sa.Column(sa.String, nullable=False)
    model_printers = orm.relationship('ModelPrinter',
                                      secondary=association_cartridge,
                                      back_populates='cartridges')
    departament = sa.Column(sa.String)


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

    def __repr__(self):
        return f'ModelPrinter={self.model}, brand="{self.brand}"'


class Printer(Base):
    __tablename__ = 'printer'
    id = sa.Column(sa.Integer, primary_key=True)
    model_id = sa.Column(sa.Integer,
                         sa.ForeignKey('model_printer.id'),
                         index=True)
    model_printer = orm.relationship("ModelPrinter", back_populates='printers')
    departament = sa.Column(sa.String)
    ip = sa.Column(sa.String, default=None)
    sn = sa.Column(sa.String, unique=True, index=True)
    is_work = sa.Column(sa.Boolean, default=True)
    is_free = sa.Column(sa.Boolean, default=False)
    repairing = sa.Column(sa.Boolean, default=True)
    qr = sa.Column(sa.String)
    histories = orm.relationship('History',
                                 back_populates='printer',
                                 cascade="all, delete",
                                 passive_deletes=True, )


class History(Base):
    __tablename__ = 'history'
    id = sa.Column(sa.Integer, primary_key=True)
    printer_id = sa.Column(sa.Integer,
                           sa.ForeignKey('printer.id', ondelete="CASCADE"),
                           index=True)
    printer = orm.relationship('Printer', back_populates='histories')
    date = sa.Column(sa.DateTime)
    description = sa.Column(sa.Text)
    author_id = sa.Column(sa.Integer,
                          sa.ForeignKey('users.id'),
                          index=True)
    author = orm.relationship('User', back_populates="histories")
