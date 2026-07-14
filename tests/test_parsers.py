import unittest

from mapkit import parse_decimal


class ParseDecimalTests(unittest.TestCase):
    def test_decimal_formats(self) -> None:
        cases = {
            "1234.56": "1234.56",
            "1234,56": "1234.56",
            "1,234,567.89": "1234567.89",
            "1.234.567,89": "1234567.89",
            "1 234 567,89": "1234567.89",
            "1\u00a0234\u00a0567,89": "1234567.89",
            "1'234'567.89": "1234567.89",
            "1,234": "1234",
            "+1234,50": "1234.50",
            "(1 234,50)": "-1234.50",
            "1.23e+6": "1230000",
            "0.0000006": "0.0000006",
            "0.6e-6": "0.0000006",
            "  0,001  ": "0.001",
        }

        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(parse_decimal(value), expected)

    def test_invalid_values(self) -> None:
        values = (
            "",
            " ",
            "not-a-number",
            ".",
            ",",
            "+",
            "-",
            "()",
            "--1",
            "7.0a",
            "1.2.3",
            "1,,234",
            "12,34,567",
            "1 23 456",
        )
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_decimal(value)
