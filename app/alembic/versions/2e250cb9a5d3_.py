"""empty message

Revision ID: 2e250cb9a5d3
Revises: 36929c8de589
Create Date: 2022-07-26 08:35:25.346435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e250cb9a5d3'
down_revision = '36929c8de589'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # op.add_column(
    #     'printer',
    #     sa.Column('location', sa.String), ),
    pass


def downgrade() -> None:
    op.drop_column('printer', 'location')
