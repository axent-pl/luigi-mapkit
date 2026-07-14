# Contributing

## Setup

This project uses Python 3.13 or newer and supports `uv` for environment and
lock-file management.

```console
uv sync
```

## Tests

Run the complete test suite before submitting a change:

```console
uv run python -m unittest discover -s tests -v
```

## Build

Build both the source distribution and wheel:

```console
uv build
```

The resulting archives are placed in `dist/`.
