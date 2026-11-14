from collections.abc import Iterator

from fastapi import Request
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.utils.database_errors import translate_database_error


def get_db(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        try:
            yield session
        except DBAPIError as exc:
            session.rollback()
            translate_database_error(exc, "database")
