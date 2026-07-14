# User guide

## Mapping a CSV

A mapper is a callable with the following shape:

```python
mapper(row) -> value
```

The keys in the mapper dictionary become output column names. Dictionary
insertion order determines output column order.

```python
import luigi

from mapkit import column_value, decimal_mapper, process_data


mappers = {
    "customer_name": column_value("name"),
    "invoice_number": column_value("invoice_no"),
    "amount": decimal_mapper("raw_amount"),
}

process_data(
    input=luigi.LocalTarget("in.csv"),
    output=luigi.LocalTarget("out.csv"),
    mappers=mappers,
)
```

For this input:

```text
name;invoice_no;raw_amount
Ada;INV-17;1 234,50
```

the output is:

```text
customer_name,invoice_number,amount
Ada,INV-17,1234.50
```

`process_data` detects the input dialect. Output uses Python's default CSV
dialect: comma-separated fields with CRLF record endings.

## Base mappers

### Column values

`column_value` reads an input column without changing its value:

```python
from mapkit import column_value

name = column_value("source_name")
```

An empty field produces `""`, and a short CSV row can produce `None`. A missing
header raises `MissingInputColumn`.

### Decimals

`decimal_mapper` validates a required decimal and returns a normalized string:

| Input | Output |
|---|---|
| `1234.56` | `1234.56` |
| `1234,56` | `1234.56` |
| `1,234,567.89` | `1234567.89` |
| `1.234.567,89` | `1234567.89` |
| `(1 234,50)` | `-1234.50` |
| `1.23e+6` | `1230000` |

Malformed grouping raises `InvalidInputValue` instead of silently changing the
number.

The underlying `parse_decimal(value)` parser is also public. It returns the
same normalized string and raises `ValueError` for malformed input, making it
available for composition with `transform` or for use outside CSV mappers.

## Combining mappers

Combinators wrap other mappers. Read a nested expression from the inside out:

```python
from mapkit import column_value, is_one_of, is_required, transform

status = is_one_of(
    transform(is_required(column_value("raw_status")), str.casefold),
    ("new", "paid", "cancelled"),
)
```

This reads `raw_status`, rejects an empty value, converts it to lowercase, and
then checks the allow-list.

### Required values

`is_required` rejects `None`, empty strings, and whitespace-only strings:

```python
from mapkit import column_value, is_required

name = is_required(column_value("name"))
```

### Default values

`default` substitutes a value for an empty result:

```python
from mapkit import column_value, default

country = default(column_value("country"), "PL")
```

It does not catch mapping errors, so a missing header is not silently replaced.
Apply a default before a transformation that cannot accept `None`:

```python
from mapkit import column_value, default, transform

country = transform(default(column_value("country"), "PL"), str.upper)
```

### Transformations

`transform` passes a mapped result to a function:

```python
from mapkit import column_value, is_required, transform

name = transform(is_required(column_value("name")), str.strip)
count = transform(is_required(column_value("count")), int)
```

A `ValueError` from the function becomes `InvalidInputValue`. Other unexpected
exceptions propagate unchanged.

### Allowed values

`is_one_of` requires the mapped value to belong to an allow-list. Normalize
before validating:

```python
from mapkit import column_value, is_one_of, is_required, transform

status = is_one_of(
    transform(is_required(column_value("status")), str.casefold),
    ("active", "inactive"),
)
```

### Fallbacks

`fallback` tries alternatives from left to right:

```python
from mapkit import column_value, fallback, is_required

display_name = fallback(
    is_required(column_value("preferred_name")),
    is_required(column_value("legal_name")),
    lambda row: "Unknown",
)
```

Only `MappingError` triggers the next mapper. Unexpected programming or system
errors are not swallowed.

## Errors

All expected data-quality failures derive from `MappingError`:

- `MissingInputColumn` means a configured input header is absent.
- `InvalidInputValue` means a value does not satisfy its mapper.

When raised by `process_data`, an error is enriched with its output column,
record number, and CSV line number.
