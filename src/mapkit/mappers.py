"""Base mappers and combinators for transforming CSV rows."""

from collections.abc import Callable, Iterable, Mapping
from functools import wraps
from typing import Any, TypeVar, cast

from .errors import InvalidInputValue, MappingError, MissingInputColumn
from .parsers import parse_decimal

RowValue = str | None
Row = Mapping[str | None, RowValue | list[str]]
T = TypeVar("T")
U = TypeVar("U")
Mapper = Callable[[Row], T]


def _input_column(mapper: Mapper[Any]) -> str | None:
    return cast(str | None, getattr(mapper, "input_column", None))


def _with_input_column(mapper: Mapper[T], column: str | None) -> Mapper[T]:
    # Functions and the wrappers created below support attributes. User-defined
    # callable objects need not, so metadata is best-effort.
    try:
        setattr(mapper, "input_column", column)
    except (AttributeError, TypeError):
        pass
    return mapper


def transform(mapper: Mapper[T], function: Callable[[T], U]) -> Mapper[U]:
    """Apply a value transformation to the result of another mapper."""

    @wraps(mapper)
    def map_transformed(row: Row) -> U:
        value = mapper(row)
        try:
            return function(value)
        except MappingError:
            raise
        except ValueError as exc:
            raise InvalidInputValue(
                input_column=_input_column(mapper),
                value=value,
                reason=str(exc) or type(exc).__name__,
            ) from exc

    return _with_input_column(map_transformed, _input_column(mapper))


def is_required(mapper: Mapper[T | None]) -> Mapper[T]:
    """Reject None, an empty string, or a whitespace-only string."""

    @wraps(mapper)
    def map_is_required(row: Row) -> T:
        value = mapper(row)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise InvalidInputValue(
                input_column=_input_column(mapper),
                value=value,
                reason="required value is empty",
            )
        return value

    return _with_input_column(map_is_required, _input_column(mapper))


def default(mapper: Mapper[T | None], default_value: U) -> Mapper[T | U]:
    """Replace a None, empty, or whitespace-only result with a default."""

    @wraps(mapper)
    def map_default(row: Row) -> T | U:
        value = mapper(row)
        if value is None or (isinstance(value, str) and not value.strip()):
            return default_value
        return value

    return _with_input_column(map_default, _input_column(mapper))


def is_one_of(mapper: Mapper[T], allowed_values: Iterable[T]) -> Mapper[T]:
    """Require a mapped value to be one of the configured values."""
    allowed = tuple(allowed_values)

    @wraps(mapper)
    def map_is_one_of(row: Row) -> T:
        value = mapper(row)
        if value not in allowed:
            raise InvalidInputValue(
                input_column=_input_column(mapper),
                value=value,
                reason=f"expected one of {allowed!r}",
            )
        return value

    return _with_input_column(map_is_one_of, _input_column(mapper))


def fallback(*mappers: Mapper[T]) -> Mapper[T]:
    """Return the first successfully mapped value.

    Only expected :class:`MappingError` instances trigger the next mapper.
    Programming errors and other unexpected exceptions are not swallowed.
    """
    if not mappers:
        raise ValueError("fallback requires at least one mapper")

    def map_fallback(row: Row) -> T:
        errors: list[MappingError] = []
        for mapper in mappers:
            try:
                return mapper(row)
            except MappingError as exc:
                errors.append(exc)

        last_error = errors[-1]
        reasons = "; ".join(error.reason for error in errors)
        raise InvalidInputValue(
            input_column=last_error.input_column,
            value=last_error.value,
            reason=f"all fallback mappers failed: {reasons}",
        ) from last_error

    columns = {_input_column(mapper) for mapper in mappers}
    column = columns.pop() if len(columns) == 1 else None
    return _with_input_column(map_fallback, column)


def column_value(column: str) -> Mapper[str | None]:
    """Read a value from an input column."""

    def map_column(row: Row) -> str | None:
        try:
            value = row[column]
        except KeyError as exc:
            raise MissingInputColumn(
                input_column=column,
                reason="input column is missing",
            ) from exc
        if isinstance(value, list):
            raise InvalidInputValue(
                input_column=column,
                value=value,
                reason="input row contains surplus fields",
            )
        return value

    return _with_input_column(map_column, column)


def decimal_mapper(column: str) -> Mapper[str]:
    """Read and normalize a required decimal value from an input column."""
    return transform(is_required(column_value(column)), parse_decimal)
