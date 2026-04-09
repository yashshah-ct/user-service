revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import text
    from alembic import op
    op.execute(text("""
        CREATE TABLE users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """))
    op.execute(text("CREATE INDEX ix_users_email ON users (email)"))


def downgrade() -> None:
    from sqlalchemy import text
    from alembic import op
    op.execute(text("DROP TABLE IF EXISTS users"))
