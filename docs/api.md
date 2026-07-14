# API reference

The supported public API is exported directly from `mapkit`.

## Types

- `Row`: the mapping passed to a mapper.
- `RowValue`: a string or `None` input value.
- `Mapper[T]`: a callable that maps a `Row` to `T`.

## Mappers and combinators

- `column_value(column)`: read an input column.
- `decimal_mapper(column)`: parse and normalize a required decimal.
- `is_required(mapper)`: reject an empty result.
- `default(mapper, value)`: substitute an empty result.
- `transform(mapper, function)`: transform a mapped value.
- `is_one_of(mapper, allowed_values)`: validate membership.
- `fallback(*mappers)`: return the first successful result.

## Parsers

- `parse_decimal(value)`: parse a decimal and return its normalized string form.

## Processing

`process_data(input, output, mappers)` reads a CSV from a Luigi target and
writes the mapped CSV to another Luigi target.

## Errors

- `MappingError`: base class for expected data-quality errors.
- `InvalidInputValue`: a value failed validation or transformation.
- `MissingInputColumn`: the configured input column is absent.

Advanced users may import from `mapkit.errors`, `mapkit.mappers`, and
`mapkit.processor`, but importing the public names from `mapkit` is preferred.
