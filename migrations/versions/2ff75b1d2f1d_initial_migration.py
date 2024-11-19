"""Initial migration

Revision ID: 2ff75b1d2f1d
Revises: 
Create Date: 2024-11-18 12:09:54.739335

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2ff75b1d2f1d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('poem_details', schema=None) as batch_op:
        batch_op.drop_constraint('poem_details_poem_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'poems', ['poem_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('poem_types', schema=None) as batch_op:
        batch_op.alter_column('criteria',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=sa.JSON(),
               existing_nullable=False)

    with op.batch_alter_table('poems', schema=None) as batch_op:
        batch_op.create_unique_constraint('_poem_title_poet_uc', ['title', 'poet_id'])

    with op.batch_alter_table('poets', schema=None) as batch_op:
        batch_op.drop_column('is_deleted')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('poets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_deleted', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True))

    with op.batch_alter_table('poems', schema=None) as batch_op:
        batch_op.drop_constraint('_poem_title_poet_uc', type_='unique')

    with op.batch_alter_table('poem_types', schema=None) as batch_op:
        batch_op.alter_column('criteria',
               existing_type=sa.JSON(),
               type_=postgresql.JSONB(astext_type=sa.Text()),
               existing_nullable=False)

    with op.batch_alter_table('poem_details', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('poem_details_poem_id_fkey', 'poems', ['poem_id'], ['id'])

    # ### end Alembic commands ###