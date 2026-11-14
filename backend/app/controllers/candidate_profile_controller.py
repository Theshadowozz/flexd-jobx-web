from app.schemas.candidate_profile import CandidateProfileRead
from app.services import candidate_profile_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_candidate_profiles(db, limit, offset):
    records, total = await service.list_candidate_profiles(db, limit, offset)
    return list_response(
        "Candidate profiles retrieved",
        "candidate_profiles",
        [CandidateProfileRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_candidate_profile(db, record_id):
    record = await service.get_candidate_profile(db, record_id)
    return item_response(
        "Candidate profile retrieved",
        "candidate_profile",
        CandidateProfileRead.model_validate(record),
    )


async def create_candidate_profile(db, schema):
    record = await service.create_candidate_profile(db, schema)
    return item_response(
        "Candidate profile created",
        "candidate_profile",
        CandidateProfileRead.model_validate(record),
    )


async def update_candidate_profile(db, record_id, schema):
    record = await service.update_candidate_profile(db, record_id, schema)
    return item_response(
        "Candidate profile updated",
        "candidate_profile",
        CandidateProfileRead.model_validate(record),
    )


async def delete_candidate_profile(db, record_id):
    await service.delete_candidate_profile(db, record_id)
    return empty_response("Candidate profile deleted")
