"""Add categories table and item category_id foreign key

Revision ID: 002
Revises: 001
Create Date: 2026-06-27

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_items_category_id"), ["category_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_items_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
        )
        batch_op.drop_column("category")


def downgrade() -> None:
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("category", sa.String(length=100), nullable=True),
        )
        batch_op.drop_constraint("fk_items_category_id_categories", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_items_category_id"))
        batch_op.drop_column("category_id")

    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
