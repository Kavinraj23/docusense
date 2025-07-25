"""Add user_id as UUID to Syllabus model

Revision ID: 5e830b3c03a8
Revises: 4abf269fed97
Create Date: 2025-06-24 13:52:31.363250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e830b3c03a8'
down_revision: Union[str, None] = '4abf269fed97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('syllabi', sa.Column('user_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'syllabi', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'syllabi', type_='foreignkey')
    op.drop_column('syllabi', 'user_id')
    # ### end Alembic commands ###
