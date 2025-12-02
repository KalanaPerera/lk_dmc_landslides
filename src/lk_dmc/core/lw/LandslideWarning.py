import os
from dataclasses import dataclass

from utils import JSONFile, Log

from .LandSlideWarningPDFMixin import LandSlideWarningPDFMixin
from .LandSlideWarningRemoteMixin import LandSlideWarningRemoteMixin

log = Log("LandslideWarning")


@dataclass
class LandslideWarning(LandSlideWarningPDFMixin, LandSlideWarningRemoteMixin):
    date_id: str
    level_to_district_to_dsds: dict[int, dict[str, list[str]]]

    def get_level_to_n_warnings(self) -> dict[int, int]:
        return {
            threat_level: sum(
                len(dsd_id_list) for dsd_id_list in district_to_dsds.values()
            )
            for threat_level, district_to_dsds in self.level_to_district_to_dsds.items()  # noqa: E501
        }

    def len(self) -> int:
        return sum(self.get_level_to_n_warnings().values())

    @classmethod
    def get_json_path(cls, date_id) -> str:
        decade = date_id[0:3] + "0s"
        year = date_id[0:4]
        year_and_month = date_id[0:7]
        return os.path.join(
            cls.DIR_DATA_JSONS,
            decade,
            year,
            year_and_month,
            f"{date_id}.json",
        )

    @property
    def json_path(self) -> str:
        return self.get_json_path(self.date_id)

    @classmethod
    def from_json(cls, json_path) -> "LandslideWarning":
        d = JSONFile(json_path).read()
        return cls(**d)
