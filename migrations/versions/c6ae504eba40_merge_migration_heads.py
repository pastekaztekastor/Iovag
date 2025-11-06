"""merge migration heads

Revision ID: c6ae504eba40
Revises: 1760a83678c9, d4f5a6b7c8d9
Create Date: 2025-11-06 09:21:32.902559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6ae504eba40'
down_revision = ('1760a83678c9', 'd4f5a6b7c8d9')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
