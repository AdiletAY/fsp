from src.schema import BaseSchema


class DduContractor(BaseSchema):
    ddu_contractor_id: int
    ddu_contractor_name: str
    bin: str
    address: str
    bank_name: str
    iik: str
    bik: str
    director_fio: str
    # guid: UUID
