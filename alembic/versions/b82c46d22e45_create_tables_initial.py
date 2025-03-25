"""Create tables initial

Revision ID: b82c46d22e45
Revises: 0f94cec9acfe
Create Date: 2025-03-25 22:18:23.660504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b82c46d22e45'
down_revision = '0f94cec9acfe'
branch_labels = None
depends_on = None


from app.models.base import Base
from app.models.user import User
from app.models.program import Program
from app.models.session import Session
from app.models.booking import Booking

# revision identifiers, used by Alembic.



def upgrade():
    # Create all tables based on your SQLAlchemy models
    Base.metadata.create_all(bind=op.get_bind())


def downgrade():
    # Drop all tables
    Base.metadata.drop_all(bind=op.get_bind())
