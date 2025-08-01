"""Add bottle tracking fields to Batch model

Revision ID: c6111a50522d
Revises: 22a461fb2313
Create Date: 2025-08-02 09:23:34.388043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6111a50522d'
down_revision = '22a461fb2313'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('batch', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bottle_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('bottle_volume', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('bottle_volume_unit', sa.String(length=10), nullable=False, server_default='ml'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('batch', schema=None) as batch_op:
        batch_op.drop_column('bottle_volume_unit')
        batch_op.drop_column('bottle_volume')
        batch_op.drop_column('bottle_count')

    # ### end Alembic commands ###
