import tempfile
import unittest
from pathlib import Path

import luigi
import openpyxl

from mapkit import convert


class ConverterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)

    def target(self, name: str) -> luigi.LocalTarget:
        return luigi.LocalTarget(str(self.directory / name))

    def create_workbook(self, filename: str, sheets: dict[str, list[list[object]]]) -> luigi.LocalTarget:
        target = self.target(filename)
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)

        for sheet_name, rows in sheets.items():
            worksheet = workbook.create_sheet(sheet_name)
            for row in rows:
                worksheet.append(row)

        workbook.save(target.path)
        return target

    def test_default_uses_first_sheet(self) -> None:
        input_target = self.create_workbook(
            "input.xlsx",
            {
                "first": [["name", "age"], ["Ada", 31]],
                "second": [["name", "age"], ["Borg", 22]],
            },
        )
        output_target = self.target("output.csv")

        convert(input_target, output_target)

        self.assertEqual(
            Path(output_target.path).read_text(encoding="utf-8"),
            "name,age\nAda,31\n",
        )

    def test_sheet_name_selects_named_sheet(self) -> None:
        input_target = self.create_workbook(
            "input.xlsx",
            {
                "default": [["name", "age"], ["Ada", 31]],
                "other": [["name", "age"], ["Borg", 22]],
            },
        )
        output_target = self.target("output.csv")

        convert(input_target, output_target, sheet_name="other")

        self.assertEqual(
            Path(output_target.path).read_text(encoding="utf-8"),
            "name,age\nBorg,22\n",
        )

    def test_filter_is_applied(self) -> None:
        input_target = self.create_workbook(
            "input.xlsx",
            {
                "data": [["name", "age"], ["Ada", 31], ["Borg", 22]],
            },
        )
        output_target = self.target("output.csv")

        convert(
            input_target,
            output_target,
            row_filter=lambda row: row["age"] is not None and row["age"] > 25,
        )

        self.assertEqual(
            Path(output_target.path).read_text(encoding="utf-8"),
            "name,age\nAda,31\n",
        )
