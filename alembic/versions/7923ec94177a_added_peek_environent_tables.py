"""Added Peek Environent tables

Revision ID: 7923ec94177a
Revises: bc1622f6c16c
Create Date: 2016-12-03 16:58:10.013775

"""

# revision identifiers, used by Alembic.
revision = '7923ec94177a'
down_revision = 'bc1622f6c16c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('PeekEnvServer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('ip', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ip'),
    sa.UniqueConstraint('name'),
    schema='peek_server'
    )
    op.create_table('PeekEnvAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('serverId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['serverId'], ['peek_server.PeekEnvServer.id'], ),
    sa.PrimaryKeyConstraint('id', 'serverId'),
    sa.UniqueConstraint('ip'),
    sa.UniqueConstraint('name'),
    schema='peek_server'
    )
    op.create_table('PeekEnvClient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('serverId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['serverId'], ['peek_server.PeekEnvServer.id'], ),
    sa.PrimaryKeyConstraint('id', 'serverId'),
    sa.UniqueConstraint('ip'),
    sa.UniqueConstraint('name'),
    schema='peek_server'
    )
    op.create_table('PeekEnvWorker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('ip', sa.String(), nullable=True),
    sa.Column('serverId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['serverId'], ['peek_server.PeekEnvServer.id'], ),
    sa.PrimaryKeyConstraint('id', 'serverId'),
    sa.UniqueConstraint('ip'),
    sa.UniqueConstraint('name'),
    schema='peek_server'
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('PeekEnvWorker', schema='peek_server')
    op.drop_table('PeekEnvClient', schema='peek_server')
    op.drop_table('PeekEnvAgent', schema='peek_server')
    op.drop_table('PeekEnvServer', schema='peek_server')
    ### end Alembic commands ###
