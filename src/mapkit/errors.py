"""Errors raised for expected mapping and data-quality failures."""


class MappingError(ValueError):
    """An expected data-quality error raised while mapping one CSV value."""

    def __init__(
        self,
        *,
        reason: str,
        input_column: str | None = None,
        value: object | None = None,
        output_column: str | None = None,
        record: int | None = None,
        line: int | None = None,
    ) -> None:
        super().__init__(reason)
        self.reason = reason
        self.input_column = input_column
        self.value = value
        self.output_column = output_column
        self.record = record
        self.line = line

    def add_context(
        self, *, output_column: str, record: int, line: int
    ) -> "MappingError":
        """Add processor context without overwriting mapper-specific context."""
        if self.output_column is None:
            self.output_column = output_column
        if self.record is None:
            self.record = record
        if self.line is None:
            self.line = line
        return self

    def __str__(self) -> str:
        fields = (
            ("output_column", self.output_column),
            ("input_column", self.input_column),
            ("record", self.record),
            ("line", self.line),
            ("value", self.value),
            ("reason", self.reason),
        )
        details = " | ".join(
            f"{name}={value!r}" for name, value in fields if value is not None
        )
        return f"{type(self).__name__}: {details}"


class InvalidInputValue(MappingError):
    """An input value cannot be mapped according to the configured rules."""


class MissingInputColumn(MappingError):
    """A mapper's configured input column is absent from a row."""
