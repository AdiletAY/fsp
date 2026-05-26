from typing import Annotated

from fastapi import Depends
from src.database.deps import DatabaseConnectionDep

from .repo import DduContractorRepository
from .service import DduContractorService


def get_ddu_contractor_service(
    connection: DatabaseConnectionDep,
) -> DduContractorService:
    ddu_contractor_repository = DduContractorRepository(connection=connection)
    return DduContractorService(ddu_contractor_repository=ddu_contractor_repository)


DduContractorServiceDep = Annotated[
    DduContractorService,
    Depends(get_ddu_contractor_service),
]
