"""empty message

Revision ID: 0b55bccde77a
Revises: ab9dc374a915
Create Date: 2022-09-19 20:47:03.592365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b55bccde77a'
down_revision = 'ab9dc374a915'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'department',
        sa.Column('service', sa.Boolean), ),


def downgrade() -> None:
    op.drop_column('department', 'service')