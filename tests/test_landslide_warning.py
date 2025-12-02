import os
import unittest

from lk_dmc import LandslideWarning


class TestCase(unittest.TestCase):

    def test_from_pdf(self):
        lw = LandslideWarning.from_pdf(
            os.path.join("tests", "inputs", "2025-12-02.pdf"),
            force_parse_pdf=True,
        )
        self.assertIsInstance(lw, LandslideWarning)
        self.assertEqual(lw.date_id, "2025-12-02")
        self.assertEqual(lw.get_level_to_n_warnings(), {1: 18, 2: 0, 3: 63})

        kandy_level_3 = lw.level_to_district_to_dsds[3]["LK-21"]
        self.assertEqual(
            kandy_level_3,
            [
                "LK-2103",
                "LK-2106",
                "LK-2109",
                "LK-2112",
                "LK-2115",
                "LK-2118",
                "LK-2121",
                "LK-2127",
                "LK-2133",
                "LK-2134",
                "LK-2136",
                "LK-2139",
                "LK-2142",
                "LK-2145",
                "LK-2148",
                "LK-2151",
                "LK-2154",
                "LK-2154",
                "LK-2157",
            ],
        )
        self.assertEqual(kandy_level_3, sorted(kandy_level_3))

    def test_list_from_remote(self):
        n_limit = 10
        lw_list = LandslideWarning.list_from_remote(n_limit)
        self.assertIsInstance(lw_list, list)
        self.assertEqual(len(lw_list), n_limit)
