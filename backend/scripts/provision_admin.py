"""Explicit operator command. Never runs at application startup."""

import argparse
import getpass
import ssl

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.configs.settings import get_settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import create_user


def main():
    parser = argparse.ArgumentParser(description="Provision first JobX administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Admin password (minimum 12 characters): ")
    if password != getpass.getpass("Repeat password: "):
        parser.error("Passwords do not match")
    payload = UserCreate(name=args.name, email=args.email, password=password, account_type="admin")
    settings = get_settings()
    transport = (
        {"ssl_disabled": True}
        if settings.db_ssl_disabled
        else {
            "ssl": ssl.create_default_context(
                cafile=str(settings.db_ssl_ca) if settings.db_ssl_ca else None
            )
        }
    )
    print(f"Target database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    if (
        input("This command writes an admin account. Type CREATE ADMIN to proceed: ")
        != "CREATE ADMIN"
    ):
        parser.exit(message="Cancelled\n")
    engine = create_engine(settings.database_url, connect_args={**transport, "connect_timeout": 5})
    try:
        with Session(engine) as db:
            if db.scalar(select(User.id).where(User.account_type == "admin").limit(1)) is not None:
                parser.exit(message="Admin already exists; use authenticated account management.\n")
            user = create_user(db, payload)
            print(f"Admin created: ID {user.id}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
