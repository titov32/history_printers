"""empty message

Revision ID: 7676b3b045ae
Revises: 9391cb99878d
Create Date: 2022-09-23 13:35:16.520631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7676b3b045ae'
down_revision = '9391cb99878d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq__model_printer_cartridge",
                                "association_cartridge",
                                ["model_printer_id", "cartridge_id"])


def downgrade() -> None:
    op.drop_unique_constraint('uq__model_printer_cartridge',
                              'association_cartridge')
