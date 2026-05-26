from typing import Sequence

from src.repository import BaseRepository

from .schemas import DduContractor


class DduContractorRepository(BaseRepository):
    async def list_ddu_contractor(self) -> Sequence[DduContractor]:
        rows = await self.call_sp("public.list_ddu_contractor", cursor=True)
        return [DduContractor.model_validate(row) for row in rows]
