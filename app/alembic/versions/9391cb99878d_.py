"""empty message

Revision ID: 9391cb99878d
Revises: 0b55bccde77a
Create Date: 2022-09-21 13:13:58.844135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9391cb99878d'
down_revision = '0b55bccde77a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'history',
        sa.Column('latitude', sa.String), ),
    op.add_column(
        'history',
        sa.Column('longitude', sa.String), ),


def downgrade() -> None:
    op.drop_column('history', 'latitude')
    op.drop_column('history', 'longitude')
