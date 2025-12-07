import os
import unittest

from lk_dmc import LandslideWarning


class TestCase(unittest.TestCase):

    def test_from_pdf(self):

        for date_id, level_to_n_warnings, must_have_dsd_id_to_level in [
            ["2025-12-03", {1: 23, 2: 30, 3: 38}, {"LK-8124": 2}],
            ["2025-12-02", {1: 18, 2: 0, 3: 68}, {"LK-8127": 3}],
            [
                "2025-12-06",
                {1: 27, 2: 23, 3: 49},
                {"LK-2303": 2, "LK-2315": 2},
            ],
            [
                "2025-12-07",
                {1: 20, 2: 30, 3: 42},
                {"LK-2221": 3, "LK-2224": 3},
            ],
        ]:
            lw = LandslideWarning.from_pdf(
                os.path.join("tests", "inputs", f"{date_id}.pdf"),
                force_parse_pdf=True,
            )
            self.assertIsInstance(lw, LandslideWarning)
            self.assertEqual(lw.date_id, date_id)
            print(lw.get_level_to_n_warnings())
            self.assertEqual(
                lw.get_level_to_n_warnings(), level_to_n_warnings
            )

            for dsd_id, level in must_have_dsd_id_to_level.items():
                district_id = dsd_id[:5]
                dsd_ids = lw.level_to_district_to_dsds.get(level, {}).get(
                    district_id, []
                )
                self.assertIn(dsd_id, dsd_ids)

    @unittest.skip("Needs network access")
    def test_list_from_remote(self):
        n_limit = 10
        lw_list = LandslideWarning.list_from_remote(n_limit)
        self.assertIsInstance(lw_list, list)
        self.assertEqual(len(lw_list), n_limit)
