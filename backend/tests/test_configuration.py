import pytest
from pydantic import TypeAdapter, ValidationError

from app.configs.settings import Settings
from app.models import Base
from app.schemas.common import UnsignedId


def test_settings_and_metadata():
    settings = Settings(_env_file=None, db_password="p@ss:/word", db_tls_enabled=False)
    assert settings.database_url.password == "p@ss:/word"
    assert settings.db_tls_enabled is False
    assert not hasattr(settings, "llm_provider")
    assert len(Base.metadata.tables) == 12
    assert list(Base.metadata.tables["candidate_profile"].primary_key.columns)[0].name == "user_id"
    assert (
        TypeAdapter(UnsignedId).dump_json(18_446_744_073_709_551_615) == b'"18446744073709551615"'
    )


def test_weak_secret_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret_key="weak")


async def test_http_errors_keep_envelope(api):
    response = await api.get("/api/v1/missing")
    assert response.status_code == 404
    assert set(response.json()) == {"message", "error", "data"}
    assert response.json()["data"] == {}
