from app.schemas.company_profile import CompanyProfileRead
from app.services import company_profile_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_company_profiles(db, limit, offset):
    records, total = await service.list_company_profiles(db, limit, offset)
    return list_response(
        "Company profiles retrieved",
        "company_profiles",
        [CompanyProfileRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_company_profile(db, record_id):
    record = await service.get_company_profile(db, record_id)
    return item_response(
        "Company profile retrieved", "company_profile", CompanyProfileRead.model_validate(record)
    )


async def create_company_profile(db, schema):
    record = await service.create_company_profile(db, schema)
    return item_response(
        "Company profile created", "company_profile", CompanyProfileRead.model_validate(record)
    )


async def update_company_profile(db, record_id, schema):
    record = await service.update_company_profile(db, record_id, schema)
    return item_response(
        "Company profile updated", "company_profile", CompanyProfileRead.model_validate(record)
    )


async def delete_company_profile(db, record_id):
    await service.delete_company_profile(db, record_id)
    return empty_response("Company profile deleted")
