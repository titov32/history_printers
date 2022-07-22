"""empty message

Revision ID: 5f8f46c9d316
Revises: 
Create Date: 2022-07-20 19:11:59.843554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f8f46c9d316'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'history',
        sa.Column('path_file', sa.String), ),



def downgrade() -> None:
    op.drop_column('printer', 'qr')