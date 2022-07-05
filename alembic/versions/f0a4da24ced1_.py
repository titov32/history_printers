"""empty message

Revision ID: f0a4da24ced1
Revises: 1cbedd5f9c86
Create Date: 2022-06-28 23:16:50.048300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0a4da24ced1'
down_revision = '1cbedd5f9c86'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'printer',
        sa.Column('sn', sa.String), ),
    op.add_column(
        'printer',
        sa.Column('is_work', sa.Boolean)),
    op.add_column(
        'printer',
        sa.Column('is_free', sa.Boolean))


def downgrade() -> None:
    op.drop_column('printer', 'sn')
    op.drop_column('printer', 'is_work')
    op.drop_column('printer', 'is_free')
