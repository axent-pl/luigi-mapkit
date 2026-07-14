import unittest

from mapkit import (
    InvalidInputValue,
    MappingError,
    MissingInputColumn,
    column_value,
    decimal_mapper,
    default,
    fallback,
    is_one_of,
    is_required,
    transform,
)


class DecimalMapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = decimal_mapper("amount")

    def test_reads_and_parses_a_required_column(self) -> None:
        self.assertEqual(self.mapper({"amount": "1 234,50"}), "1234.50")

    def test_wraps_parser_errors_as_invalid_input(self) -> None:
        with self.assertRaises(InvalidInputValue):
            self.mapper({"amount": "1.2.3"})

    def test_missing_column(self) -> None:
        with self.assertRaises(MissingInputColumn):
            self.mapper({"other": "1.25"})


class MapperCompositionTests(unittest.TestCase):
    def test_transform(self) -> None:
        mapper = transform(column_value("name"), str.upper)
        self.assertEqual(mapper({"name": "Ada"}), "ADA")

    def test_transform_wraps_value_errors(self) -> None:
        mapper = transform(column_value("count"), int)
        with self.assertRaises(InvalidInputValue) as raised:
            mapper({"count": "many"})
        self.assertEqual(raised.exception.input_column, "count")
        self.assertEqual(raised.exception.value, "many")

    def test_is_required_rejects_blank_values(self) -> None:
        mapper = is_required(column_value("name"))
        for value in (None, "", "   "):
            with self.subTest(value=value):
                with self.assertRaises(InvalidInputValue):
                    mapper({"name": value})

    def test_default_only_replaces_empty_values(self) -> None:
        mapper = default(column_value("country"), "PL")
        self.assertEqual(mapper({"country": ""}), "PL")
        self.assertEqual(mapper({"country": "DE"}), "DE")
        with self.assertRaises(MissingInputColumn):
            mapper({})

    def test_is_one_of(self) -> None:
        mapper = is_one_of(column_value("status"), ("new", "done"))
        self.assertEqual(mapper({"status": "done"}), "done")
        with self.assertRaisesRegex(InvalidInputValue, "expected one of"):
            mapper({"status": "unknown"})

    def test_fallback_uses_next_mapper_after_mapping_error(self) -> None:
        mapper = fallback(
            is_required(column_value("preferred_name")),
            is_required(column_value("name")),
        )
        self.assertEqual(mapper({"preferred_name": "", "name": "Ada"}), "Ada")

    def test_fallback_does_not_swallow_programming_errors(self) -> None:
        def broken_mapper(row):
            raise RuntimeError("bug")

        mapper = fallback(broken_mapper, column_value("name"))
        with self.assertRaisesRegex(RuntimeError, "bug"):
            mapper({"name": "Ada"})

    def test_fallback_reports_all_expected_failures(self) -> None:
        mapper = fallback(column_value("first"), column_value("second"))
        with self.assertRaisesRegex(
            InvalidInputValue, "all fallback mappers failed"
        ) as raised:
            mapper({})
        self.assertIsInstance(raised.exception.__cause__, MappingError)

    def test_fallback_requires_at_least_one_mapper(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            fallback()
