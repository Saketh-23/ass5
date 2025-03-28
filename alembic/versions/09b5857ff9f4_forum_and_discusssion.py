"""forum and discusssion

Revision ID: 09b5857ff9f4
Revises: b82c46d22e45
Create Date: 2025-03-25 23:39:15.333940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b5857ff9f4'
down_revision = 'b82c46d22e45'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_reviews_id', table_name='reviews')
    op.drop_table('reviews')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reviews',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('program_id', sa.INTEGER(), nullable=False),
    sa.Column('rating', sa.FLOAT(), nullable=False),
    sa.Column('comment', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'], unique=False)
    # ### end Alembic commands ###
