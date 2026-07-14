"""CSV processing for Luigi targets."""

import csv
from collections.abc import Mapping

import luigi

from .errors import MappingError
from .mappers import Mapper


def process_data(
    input: luigi.Target,
    output: luigi.Target,
    mappers: Mapping[str, Mapper[object]],
) -> None:
    """Map an input CSV target to an output CSV target.

    The input dialect is detected automatically. Mapping errors are enriched
    with the output column, record number, and physical CSV line number.
    """
    with input.open("r") as input_file:
        sample = input_file.read(8192)
        input_file.seek(0)

        dialect = csv.Sniffer().sniff(sample)
        reader = csv.DictReader(input_file, dialect=dialect)

        with output.open("w") as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=mappers.keys(),
            )
            writer.writeheader()

            for record, row in enumerate(reader, start=1):
                mapped_row: dict[str, object] = {}

                for output_column, mapper in mappers.items():
                    try:
                        mapped_row[output_column] = mapper(row)
                    except MappingError as exc:
                        exc.add_context(
                            output_column=output_column,
                            record=record,
                            line=reader.line_num,
                        )
                        raise

                writer.writerow(mapped_row)
