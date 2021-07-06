"""empty message

Revision ID: 534f3c7967cd
Revises: 
Create Date: 2021-07-05 11:29:06.073268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '534f3c7967cd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock',
    sa.Column('symbol', sa.String(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=False),
    sa.Column('current_price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('symbol')
    )
    op.create_table('headline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('headline', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['symbol'], ['stock.symbol'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('prediction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('close', sa.Float(), nullable=False),
    sa.Column('volume', sa.Float(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['symbol'], ['stock.symbol'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('price',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('close', sa.Float(), nullable=True),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['symbol'], ['stock.symbol'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('sentiment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('sentiment', sa.Float(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['symbol'], ['stock.symbol'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sentiment')
    op.drop_table('price')
    op.drop_table('prediction')
    op.drop_table('headline')
    op.drop_table('stock')
    # ### end Alembic commands ###
