"""Add recurring transactions, currency, and app lock."""
from alembic import op
import sqlalchemy as sa

revision = "20260828_0002"
down_revision = "20260828_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("transactions", sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("transactions", sa.Column("currency", sa.String(3), nullable=False, server_default="INR"))
    op.add_column("users", sa.Column("app_lock_hash", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("users", "app_lock_hash")
    op.drop_column("transactions", "currency")
    op.drop_column("transactions", "is_recurring")
