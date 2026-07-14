import unittest

from mapkit import date_parser, parse_date, parse_decimal


class ParseDateTests(unittest.TestCase):
    def test_date_formats(self) -> None:
        cases = {
            "2024-01-15": "2024-01-15",
            "2024-01-15 14:30:45": "2024-01-15",
            "2024-01-15 14:30:45.123456": "2024-01-15",
            "2024-01-15T14:30:45": "2024-01-15",
            "2024-01-15T14:30:45.123456": "2024-01-15",
            "2024-01-15T14:30:45+0200": "2024-01-15",
            "2024-01-15T14:30:45+02:00": "2024-01-15",
            "15.01.2024": "2024-01-15",
            "15.01.2024 14:30:45": "2024-01-15",
            "15.01.2024 14:30": "2024-01-15",
            "2024/01/15": "2024-01-15",
            "15/01/2024": "2024-01-15",
            "01/15/2024": "2024-01-15",
            "20240115": "2024-01-15",
        }

        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(parse_date(value), expected)

    def test_output_format_factory(self) -> None:
        parser = date_parser("%d/%m/%Y")
        self.assertEqual(parser("2024-01-15"), "15/01/2024")
        self.assertEqual(parser("15.01.2024"), "15/01/2024")

    def test_invalid_values(self) -> None:
        values = (
            "",
            " ",
            "not-a-date",
            "2024-13-01",
            "31.02.2024",
            "2024/13/01",
            "20241301",
        )
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_date(value)


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
