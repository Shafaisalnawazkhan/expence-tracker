"""Initial finance schema."""
from alembic import op
import sqlalchemy as sa

revision = "20260828_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("email", sa.String(255), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("transactions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("kind", sa.String(10), nullable=False), sa.Column("amount", sa.Float(), nullable=False), sa.Column("description", sa.String(255), nullable=False), sa.Column("category", sa.String(50), nullable=False), sa.Column("predicted_category", sa.String(50)), sa.Column("category_overridden", sa.Boolean(), nullable=False), sa.Column("occurred_on", sa.Date(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_occurred_on", "transactions", ["occurred_on"])
    op.create_table("budgets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("category", sa.String(50), nullable=False), sa.Column("amount", sa.Float(), nullable=False), sa.Column("month", sa.Date(), nullable=False), sa.UniqueConstraint("user_id", "category", "month", name="uq_budget_period"))
    op.create_index("ix_budgets_user_id", "budgets", ["user_id"])


def downgrade():
    op.drop_table("budgets")
    op.drop_table("transactions")
    op.drop_table("users")

