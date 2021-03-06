#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import sys, os, io
import unittest
from contextlib import contextmanager
from pydams import DAMS
from pydams.helpers import distance_hubeny, pretty_print

@contextmanager
def suppress_stdout():
    with io.open(os.devnull, mode="w", encoding="utf-8") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

class TestDAMS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _assert_address_level(self, dict_ret, dict_exp, distance_eps=100):
        self.assertEqual(dict_ret["name"], dict_exp["name"])
        self.assertEqual(dict_ret["level"], dict_exp["level"])
        geo_point_ret = [dict_ret["y"], dict_ret["x"]]
        geo_point_exp = [dict_exp["y"], dict_exp["x"]]
        dist_ret_and_exp = distance_hubeny(geo_point_ret, geo_point_exp)
        self.assertAlmostEqual(0.0, dist_ret_and_exp, delta=distance_eps)

    def _assert_geocoded_object(self, returned, expected, distance_eps=100):
        self.assertEqual(returned["score"], expected["score"])
        self.assertEqual(len(returned["candidates"]),len(expected["candidates"]))

        for cand_ret , cand_exp in zip(returned["candidates"], expected["candidates"]):
            if isinstance(cand_ret, list) and isinstance(cand_exp, list):
                for dict_ret, dict_exp in zip(cand_ret, cand_exp):
                    self._assert_address_level(dict_ret, dict_exp, distance_eps)
            elif isinstance(cand_ret, dict) and isinstance(cand_exp, dict):
                self._assert_address_level(cand_ret, cand_exp, distance_eps)
            else:
                raise AssertionError("unexpected object was passed.")

    def test_distance_hubeny_short(self):
        geo_point_x = [35.802739, 140.380034]
        geo_point_y = [35.785796, 140.392265]
        returned = distance_hubeny(geo_point_x, geo_point_y)
        expected = 2180
        self.assertAlmostEqual(returned, expected, delta=expected*0.001)

    def test_distance_hubeny_long(self):
        geo_point_x = [35.65500, 139.74472]
        geo_point_y = [36.10056, 140.09111]
        returned = distance_hubeny(geo_point_x, geo_point_y)
        expected = 58501.873
        self.assertAlmostEqual(returned, expected, delta=expected*0.001)

    def test_init_dams(self):
        ret = DAMS.init_dams()
        self.assertTrue(ret)

    def test_geocode_error_string(self):
        DAMS.init_dams()

        address = "東京都足立区/バイク/スポーツ/仲間集め"
        returned = DAMS.geocode(address)
        expected = {
            "score":0,
            "tail":"",
            "candidates":[]
        }
        self.assertEqual(returned, expected)
        # self._assert_geocoded_object(returned, expected)


    def test_geocode_level_1(self):
        DAMS.init_dams()

        address = "東京都"
        returned = DAMS.geocode(address)

        expected = {
            "score":3,
            "candidates":[
                [
                    {
                    "name":"東京都",
                    "x":139.692,
                    "y":35.6895,
                    "level":1
                    }
                ]
            ]
        }
        self._assert_geocoded_object(returned, expected)

    def test_geocode_level_3(self):
        DAMS.init_dams()

        address = "港区"
        returned = DAMS.geocode(address)

        expected = {
            "score":2,
            "candidates":[
                [
                    {
                    "name":"愛知県",
                    "x":136.907,
                    "y":35.1809,
                    "level":1
                    },
                    {
                    "name":"名古屋市",
                    "x":136.907,
                    "y":35.1809,
                    "level":3
                    },
                    {
                    "name":"港区",
                    "x":136.885,
                    "y":35.1082,
                    "level":4
                    }
                ],
                [
                    {
                    "name":"大阪府",
                    "x":135.52,
                    "y":34.6864,
                    "level":1
                    },
                    {
                    "name":"大阪市",
                    "x":135.501,
                    "y":34.6939,
                    "level":3
                    },
                    {
                    "name":"港区",
                    "x":135.461,
                    "y":34.6641,
                    "level":4
                    }
                ],
                [
                    {
                    "name":"東京都",
                    "x":139.692,
                    "y":35.6895,
                    "level":1
                    },
                    {
                    "name":"港区",
                    "x":139.752,
                    "y":35.6585,
                    "level":3
                    },
                ]
            ]
        }
        self._assert_geocoded_object(returned, expected)

    def test_geocode_simplify_level_5(self):
        DAMS.init_dams()

        address = "東京都千代田区富士見3-1-11"
        returned = DAMS.geocode_simplify(address)

        expected = {
            "score":5,
            "candidates":[
                {
                "name":"東京都千代田区富士見",
                "x":139.746558,
                "y":35.698418,
                "level":5
                }
            ]
        }
        self._assert_geocoded_object(returned, expected, distance_eps=200)

    def test_pretty_print(self):
        DAMS.init_dams()

        address = "東京都"
        returned = DAMS.geocode(address)
        with suppress_stdout():
            pretty_print(returned)

        address = "東京都千代田区富士見3-1-11"
        returned = DAMS.geocode_simplify(address)
        with suppress_stdout():
            pretty_print(returned)

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
