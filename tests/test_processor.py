import tempfile
import unittest
from pathlib import Path

import luigi

from mapkit import (
    InvalidInputValue,
    column_value,
    decimal_mapper,
    is_required,
    process_data,
)


class ProcessDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)

    def target(self, name: str) -> luigi.LocalTarget:
        return luigi.LocalTarget(str(self.directory / name))

    def test_mapping_error_contains_output_and_csv_location(self) -> None:
        input_target = self.target("invalid.csv")
        output_target = self.target("output.csv")
        Path(input_target.path).write_text(
            "raw_amount;name\n1.2.3;Ada\n", encoding="utf-8"
        )

        with self.assertRaises(InvalidInputValue) as raised:
            process_data(
                input_target,
                output_target,
                {"amount": decimal_mapper("raw_amount")},
            )

        error = raised.exception
        self.assertEqual(error.output_column, "amount")
        self.assertEqual(error.input_column, "raw_amount")
        self.assertEqual(error.record, 1)
        self.assertEqual(error.line, 2)
        self.assertEqual(error.value, "1.2.3")
        self.assertEqual(error.reason, "inconsistent decimal separators")
        self.assertEqual(
            str(error),
            "InvalidInputValue: output_column='amount' | "
            "input_column='raw_amount' | record=1 | line=2 | "
            "value='1.2.3' | reason='inconsistent decimal separators'",
        )
        self.assertFalse(output_target.exists())

    def test_successful_processing(self) -> None:
        input_target = self.target("input.csv")
        output_target = self.target("output.csv")
        Path(input_target.path).write_text(
            "raw_amount;name\n1 234,50;Ada\n", encoding="utf-8"
        )

        process_data(
            input_target,
            output_target,
            {
                "amount": decimal_mapper("raw_amount"),
                "name": is_required(column_value("name")),
            },
        )

        self.assertEqual(
            Path(output_target.path).read_bytes(),
            b"amount,name\r\n1234.50,Ada\r\n",
        )
