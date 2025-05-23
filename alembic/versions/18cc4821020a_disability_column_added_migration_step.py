"""Disability column added migration step

Revision ID: 18cc4821020a
Revises: 
Create Date: 2025-04-20 02:14:04.180658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18cc4821020a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('items', 'is_registered',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.add_column('users', sa.Column('disability', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'disability')
    op.alter_column('items', 'is_registered',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
