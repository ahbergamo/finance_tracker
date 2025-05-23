"""initial migration

Revision ID: 615f3ee0a9d2
Revises: 
Create Date: 2025-03-27 17:33:22.044213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '615f3ee0a9d2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('family',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('pre_defined_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('category_field', sa.String(length=64), nullable=False),
    sa.Column('date_field', sa.String(length=64), nullable=False),
    sa.Column('amount_field', sa.String(length=64), nullable=False),
    sa.Column('description_field', sa.String(length=255), nullable=True),
    sa.Column('positive_expense', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('account_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('category_field', sa.String(length=64), nullable=False),
    sa.Column('date_field', sa.String(length=64), nullable=False),
    sa.Column('amount_field', sa.String(length=64), nullable=False),
    sa.Column('description_field', sa.String(length=128), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.Column('positive_expense', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'family_id', name='_accounttype_family_uc')
    )
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'family_id', name='_category_family_uc')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('budget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('import_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_type', sa.String(length=64), nullable=True),
    sa.Column('field_to_match', sa.String(length=32), nullable=False),
    sa.Column('match_pattern', sa.String(length=256), nullable=False),
    sa.Column('is_transfer', sa.Boolean(), nullable=True),
    sa.Column('override_category_id', sa.Integer(), nullable=True),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
    sa.ForeignKeyConstraint(['override_category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('is_transfer', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account_types.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('budget_category_association',
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['budget_id'], ['budget.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('budget_id', 'category_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('budget_category_association')
    op.drop_table('transaction')
    op.drop_table('import_rules')
    op.drop_table('budget')
    op.drop_table('user')
    op.drop_table('category')
    op.drop_table('account_types')
    op.drop_table('pre_defined_accounts')
    op.drop_table('family')
    # ### end Alembic commands ###
