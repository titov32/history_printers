"""test revision

Revision ID: 1cbedd5f9c86
Revises: 
Create Date: 2022-06-28 16:34:31.786823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cbedd5f9c86'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
    'cartridge',
    sa.Column('departament', sa.String)
    )




def downgrade() -> None:
    op.drop_column('cartridge', 'departament')
