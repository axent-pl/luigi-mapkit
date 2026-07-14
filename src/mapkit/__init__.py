"""Composable CSV mapping and validation for Luigi pipelines."""

from .errors import InvalidInputValue, MappingError, MissingInputColumn
from .mappers import (
    Mapper,
    Row,
    RowValue,
    column_value,
    decimal_mapper,
    default,
    fallback,
    is_one_of,
    is_required,
    transform,
)
from .parsers import parse_decimal
from .processor import process_data

__version__ = "0.1.0"

__all__ = [
    "InvalidInputValue",
    "Mapper",
    "MappingError",
    "MissingInputColumn",
    "Row",
    "RowValue",
    "column_value",
    "decimal_mapper",
    "default",
    "fallback",
    "is_one_of",
    "is_required",
    "parse_decimal",
    "process_data",
    "transform",
]
