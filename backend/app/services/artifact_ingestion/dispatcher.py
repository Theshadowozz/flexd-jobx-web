from collections.abc import Mapping

from app.agents.shared.contracts import ArtifactContent, ArtifactReference, ArtifactType
from app.services.artifact_ingestion.contracts import ArtifactReader


class UnsupportedArtifactError(ValueError):
    pass


class ArtifactIngestor:
    def __init__(self, readers: Mapping[ArtifactType, ArtifactReader] | None = None):
        self._readers = dict(readers or {})

    async def read(self, reference: ArtifactReference) -> ArtifactContent:
        reader = self._readers.get(reference.artifact_type)
        if reader is None:
            raise UnsupportedArtifactError("No reader registered for this artifact type")
        return ArtifactContent.model_validate(await reader.read(reference))
