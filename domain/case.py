from datetime import date

from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from domain.entities import Entity


@dataclass
class Case(Entity):
    caseid: int
    case_number: str
    judge: str
    date_filed: date
    date_enter: date
    case_type: str

    # sub_type: str
    # date_terminated: date
    # date_termination_entered: date
    # date_dismissed: date
    # date_reopened: date
    # reopen_code: str
    # judge_id: int
    # judge_AO_code: str
    # judge_initials: str

    def dump_json(self):
        return TypeAdapter(Case).json_schema()

    def __eq__(self, other):
        if not isinstance(other, Case):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
