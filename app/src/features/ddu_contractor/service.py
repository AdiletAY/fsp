from collections.abc import Sequence
from typing import TYPE_CHECKING

from src.service import BaseService

from .schemas import DduContractor

if TYPE_CHECKING:
    from .repo import DduContractorRepository


class DduContractorService(BaseService):
    def __init__(self, ddu_contractor_repository: "DduContractorRepository") -> None:
        self.ddu_contractor_repository = ddu_contractor_repository

    async def list_ddu_contractor(self) -> Sequence[DduContractor]:
        return await self.ddu_contractor_repository.list_ddu_contractor()
