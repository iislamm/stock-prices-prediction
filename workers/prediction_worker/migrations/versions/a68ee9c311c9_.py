"""empty message

Revision ID: a68ee9c311c9
Revises: f7fce0ce23c7
Create Date: 2021-07-05 12:00:35.961278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a68ee9c311c9'
down_revision = 'f7fce0ce23c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price', sa.Column('change', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('price', 'change')
    # ### end Alembic commands ###
