import os
from dataclasses import asdict

import camelot
from gig import Ent, EntType
from utils import JSONFile, Log

log = Log("LandslideWarning")


class LandSlideWarningPDFMixin:
    @staticmethod
    def __parse_district_name__(x) -> str:
        return x[0].replace("\n", "").strip()

    @staticmethod
    def __get_extra_dsd_names__(dsd_names_all: list[str]) -> list[str]:
        # Hack
        extra_dsd_names = []

        before_to_after = {
            "Kotmale": "Kotmale",
            "Mathurata": "Hanguranketha",
            "Thalawakele": "Nuwara Eliya",
            "Nildandahinna": "Walapane",
        }

        for dsd_name in dsd_names_all:
            for before, after in before_to_after.items():
                if before in dsd_name:
                    extra_dsd_names.append(after)
        return extra_dsd_names

    @staticmethod
    def __parse_dsd_name_list__(x) -> str:
        dsd_names_all = []
        for line in x.split("\n"):
            line = line.strip()
            if line.endswith(" and"):
                line = line[:-4]
            line = line.replace(" and ", ",")
            dsd_names = line.split(",")
            dsd_names = [name.strip() for name in dsd_names]
            print(line, dsd_names)
            dsd_names_all.extend(dsd_names)

        extra_dsd_names = LandSlideWarningPDFMixin.__get_extra_dsd_names__(
            dsd_names_all
        )
        return list(set(dsd_names_all + extra_dsd_names))

    @classmethod
    def from_pdf(cls, pdf_path, force_parse_pdf=False):
        date_id = os.path.basename(pdf_path)[:-4]
        json_path = cls.get_json_path(date_id)
        if not force_parse_pdf and os.path.exists(json_path):
            return cls.from_json(json_path)

        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")

        if not tables:
            log.error(f"No tables found in {pdf_path}")
            return None

        level_to_district_to_dsds = {}
        prev_ent_district = None
        for table in tables:
            df = table.df
            for _, row in df.iterrows():
                row_values = row.tolist()

                if len(row_values) != 4:
                    continue

                district_name = cls.__parse_district_name__(row_values)
                cand_ent_districts = Ent.list_from_name_fuzzy(
                    name_fuzzy=district_name,
                    filter_ent_type=EntType.DISTRICT,
                )
                if len(cand_ent_districts) != 1:
                    if not prev_ent_district:
                        continue
                    ent_district = prev_ent_district
                else:
                    ent_district = cand_ent_districts[0]
                prev_ent_district = ent_district
                district_id = ent_district.id

                for i_col in [1, 2, 3]:
                    threat_level = i_col
                    print("-" * 64)
                    print(threat_level)
                    print("-" * 64)
                    if threat_level not in level_to_district_to_dsds:
                        level_to_district_to_dsds[threat_level] = {}

                    dsd_names = cls.__parse_dsd_name_list__(
                        row_values[threat_level]
                    )
                    ent_dsds = []
                    for dsd_name in dsd_names:
                        cand_ent_dsds = Ent.list_from_name_fuzzy(
                            name_fuzzy=dsd_name,
                            filter_ent_type=EntType.DSD,
                            filter_parent_id=ent_district.id,
                        )
                        if len(cand_ent_dsds) != 1:
                            continue
                        ent_dsd = cand_ent_dsds[0]
                        ent_dsds.append(ent_dsd)
                    dsd_ids = [ent_dsd.id for ent_dsd in ent_dsds]

                    if not dsd_ids:
                        continue

                    if (
                        district_id
                        not in level_to_district_to_dsds[threat_level]
                    ):
                        level_to_district_to_dsds[threat_level][
                            ent_district.id
                        ] = []
                    level_to_district_to_dsds[threat_level][
                        ent_district.id
                    ].extend(dsd_ids)

                    print("-" * 32)
                    print(threat_level, district_id, district_name)
                    dsd_names2 = [ent_dsd.name for ent_dsd in ent_dsds]
                    print("\t", len(dsd_names2), dsd_names2)

        for threat_level, district_dict in level_to_district_to_dsds.items():
            for district_id, dsd_list in district_dict.items():
                dsd_list.sort()

        lw = cls(
            date_id=date_id,
            level_to_district_to_dsds=level_to_district_to_dsds,
        )
        dir_json_path = os.path.dirname(json_path)
        os.makedirs(dir_json_path, exist_ok=True)
        JSONFile(json_path).write(asdict(lw))
        return lw
