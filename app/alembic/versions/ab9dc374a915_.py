"""empty message

Revision ID: ab9dc374a915
Revises: 2e250cb9a5d3
Create Date: 2022-09-10 16:08:23.893140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab9dc374a915'
down_revision = '2e250cb9a5d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'cartridge',
        sa.Column('reused', sa.Boolean), ),



def downgrade() -> None:
    op.drop_column('cartridge', 'reused')
