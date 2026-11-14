import logging


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    # Never log bound SQL values: they can contain credentials or private content.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
