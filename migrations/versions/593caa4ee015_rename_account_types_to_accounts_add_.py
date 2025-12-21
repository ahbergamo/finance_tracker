"""rename_account_types_to_accounts_add_fields

Revision ID: 593caa4ee015
Revises: 615f3ee0a9d2
Create Date: 2025-12-21 15:38:43.896972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '593caa4ee015'
down_revision = '615f3ee0a9d2'
branch_labels = None
depends_on = None


def upgrade():
    # Rename the table
    op.rename_table('account_types', 'accounts')

    # Add new columns
    op.add_column('accounts', sa.Column('account_type',
        sa.Enum('checking', 'savings', 'credit_card', 'retirement', 'brokerage', name='account_type_enum'),
        nullable=False, server_default='checking'))
    op.add_column('accounts', sa.Column('retirement_type',
        sa.Enum('traditional_401k', 'roth_401k', 'traditional_ira', 'roth_ira', 'sep_ira', '403b', name='retirement_type_enum'),
        nullable=True))
    op.add_column('accounts', sa.Column('initial_balance',
        sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'))

    # Make CSV fields nullable (for retirement/brokerage accounts that don't need them)
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('category_field', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('date_field', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('amount_field', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('description_field', existing_type=sa.String(length=128), nullable=True)

    # Update the unique constraint name
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_constraint('_accounttype_family_uc', type_='unique')
        batch_op.create_unique_constraint('_account_family_uc', ['name', 'family_id'])

    # Update the foreign key in transaction table
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'accounts', ['account_id'], ['id'])

    # Create account_balance_history table
    op.create_table('account_balance_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('as_of_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', 'as_of_date', name='unique_account_date')
    )
    op.create_index('idx_account_date', 'account_balance_history', ['account_id', 'as_of_date'], unique=False)


def downgrade():
    # Drop account_balance_history table
    op.drop_index('idx_account_date', table_name='account_balance_history')
    op.drop_table('account_balance_history')

    # Update foreign key back to account_types
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'account_types', ['account_id'], ['id'])

    # Restore unique constraint name
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_constraint('_account_family_uc', type_='unique')
        batch_op.create_unique_constraint('_accounttype_family_uc', ['name', 'family_id'])

    # Make CSV fields non-nullable again
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('category_field', existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column('date_field', existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column('amount_field', existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column('description_field', existing_type=sa.String(length=128), nullable=False)

    # Remove new columns
    op.drop_column('accounts', 'initial_balance')
    op.drop_column('accounts', 'retirement_type')
    op.drop_column('accounts', 'account_type')

    # Rename back to account_types
    op.rename_table('accounts', 'account_types')
