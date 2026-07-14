import unittest

import mapkit


class PublicApiTests(unittest.TestCase):
    def test_version_is_exposed(self) -> None:
        self.assertEqual(mapkit.__version__, "0.1.0")

    def test_documented_api_is_exposed(self) -> None:
        for name in mapkit.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(mapkit, name))

    def test_renamed_and_removed_api(self) -> None:
        for name in ("column_value", "is_one_of", "is_required", "parse_decimal"):
            with self.subTest(name=name):
                self.assertIn(name, mapkit.__all__)

        for name in ("non_empty", "one_of", "required", "string_mapper"):
            with self.subTest(name=name):
                self.assertNotIn(name, mapkit.__all__)
                self.assertFalse(hasattr(mapkit, name))
