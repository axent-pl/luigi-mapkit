# mapkit

`mapkit` is a small Python library for building composable CSV mappings in
Luigi pipelines. Each output column is assigned a mapper that reads, validates,
or transforms values from an input row.

```python
import luigi

from mapkit import column_value, decimal_mapper, is_required, process_data, transform


mappers = {
    "customer": transform(is_required(column_value("name")), str.upper),
    "amount": decimal_mapper("raw_amount"),
}

process_data(
    input=luigi.LocalTarget("in.csv"),
    output=luigi.LocalTarget("out.csv"),
    mappers=mappers,
)
```

The input CSV dialect is detected automatically. Expected data-quality errors
include the input and output columns, record number, physical CSV line, value,
and reason.

## Installation

Install the project from its repository:

```console
python -m pip install .
```

For development with [uv](https://docs.astral.sh/uv/):

```console
uv sync
uv run python -m unittest discover -s tests -v
uv build
```

## Documentation

- [User guide](docs/guide.md)
- [API reference](docs/api.md)
- [Contributing](CONTRIBUTING.md)

## Package layout

```text
src/mapkit/          library package
tests/               unit and integration tests
docs/                user and API documentation
pyproject.toml       package and build configuration
```
