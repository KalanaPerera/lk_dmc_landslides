"""README generator for landslide warnings."""

import matplotlib.pyplot as plt
from gig import Ent, EntType
from utils import File, Log

from lk_dmc.core.lw.LandslideWarning import LandslideWarning
from lk_dmc.core.ThreatLevel import ThreatLevel

log = Log("ReadMe")


class ReadMe:
    PATH = "README.md"
    URL_LWS = (
        "https://www.dmc.gov.lk/index.php"
        + "?option=com_dmcreports&view=reports"
        + "&Itemid=276&report_type_id=5&lang=en"
    )

    def __init__(self):
        self.lw_list = LandslideWarning.list_all()

    def get_lines_for_header(self) -> list[str]:
        return [
            "# 🇱🇰 Sri Lanka: Landslide Warnings\n",
            "",
            f"From the [Disaster Management Centre]({self.URL_LWS}).",
            "",
        ]

    def get_lines_for_latest(self) -> list[str]:
        latest_lw = self.lw_list[0]
        lines = [
            f"## Latest Warnings ({latest_lw.date_id})",
            "",
        ]

        for (
            level,
            district_to_dsds,
        ) in latest_lw.level_to_district_to_dsds.items():
            threat_level = ThreatLevel.from_level(level)
            lines.extend(
                [
                    f"### {threat_level.emoji}"
                    + f' Level {level} - "{threat_level.description}"',
                    "",
                ]
            )
            for district_id, dsd_id_list in district_to_dsds.items():
                ent_district = Ent.from_id(district_id)
                lines.extend(
                    [f"#### `{district_id}` {ent_district.name}", ""]
                )
                for dsd_id in dsd_id_list:
                    ent_dsd = Ent.from_id(dsd_id)
                    lines.append(f"- `{dsd_id}` {ent_dsd.name}")
                lines.append("")
        return lines

    def get_lines_for_chart(self) -> list[str]:
        latest_lw = self.lw_list[0]

        dsd_to_level = {}
        for (
            level,
            district_to_dsds,
        ) in latest_lw.level_to_district_to_dsds.items():
            for dsd_id_list in district_to_dsds.values():
                for dsd_id in dsd_id_list:
                    dsd_to_level[dsd_id] = int(level)

        dsd_ents = Ent.list_from_type(EntType.DSD)

        fig, ax = plt.subplots(figsize=(12, 12))
        for ent in dsd_ents:
            level = dsd_to_level.get(ent.id, 0)
            geo = ent.geo()
            color = ["#FFFFFF", "#FFFF00", "#FFA500", "#FF0000"][level]
            geo.plot(ax=ax, color=color, edgecolor="#888888", linewidth=0.5)

        plt.title(
            f"Landslide Warnings in Sri Lanka on {latest_lw.date_id}",
            fontsize=16,
        )
        image_path = "landslide_warning_map.png"
        plt.savefig(image_path, dpi=300)
        plt.close()
        log.info(f"Wrote {File(image_path)}")

        lines = [
            "## Landslide Warning Map",
            "",
            f"![Landslide Warning Map]({image_path})",
            "",
        ]
        return lines

    def get_lines(self) -> str:
        return (
            self.get_lines_for_header()
            + self.get_lines_for_chart()
            + self.get_lines_for_latest()
        )

    def build(self) -> None:
        lines = self.get_lines()
        readme_file = File(self.PATH)
        readme_file.write_lines(lines)
        log.info(f"Wrote {readme_file}")
