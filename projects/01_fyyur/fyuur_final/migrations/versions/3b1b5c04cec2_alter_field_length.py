"""alter field length

Revision ID: 3b1b5c04cec2
Revises: c96301e72add
Create Date: 2020-12-22 15:56:08.586751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b1b5c04cec2'
down_revision = 'c96301e72add'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
