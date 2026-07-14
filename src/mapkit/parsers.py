"""Value parsers for use with mapper transformations."""

from decimal import Decimal, InvalidOperation


def parse_decimal(value: str) -> str:
    """Parse a decimal value and return its normalized string form."""
    original = value
    value = value.strip()
    if not value:
        raise ValueError("value is empty")

    accounting_negative = value.startswith("(") and value.endswith(")")
    if accounting_negative:
        value = value[1:-1].strip()
    elif "(" in value or ")" in value:
        raise ValueError("unmatched accounting parentheses")

    sign = ""
    if value[:1] in {"+", "-"}:
        sign, value = value[0], value[1:]
    if accounting_negative:
        if sign:
            raise ValueError("a sign is not allowed inside accounting parentheses")
        sign = "-"

    exponent = ""
    exponent_positions = [
        index for index, character in enumerate(value) if character in "eE"
    ]
    if exponent_positions:
        if len(exponent_positions) != 1:
            raise ValueError("invalid decimal exponent")
        exponent_at = exponent_positions[0]
        candidate = value[exponent_at + 1 :]
        if not candidate or not candidate.lstrip("+-").isdigit():
            raise ValueError("invalid decimal exponent")
        exponent = "e" + candidate
        value = value[:exponent_at]

    allowed_characters = "0123456789., '\u00a0"
    if not value or any(character not in allowed_characters for character in value):
        raise ValueError("unsupported decimal format")

    dot_count = value.count(".")
    comma_count = value.count(",")
    decimal_character: str | None = None

    if dot_count and comma_count:
        decimal_character = "." if value.rfind(".") > value.rfind(",") else ","
        if value.count(decimal_character) != 1:
            raise ValueError("inconsistent decimal separators")
    elif dot_count or comma_count:
        separator = "." if dot_count else ","
        groups = value.split(separator)
        count = dot_count or comma_count
        looks_grouped = (
            all(group.isdigit() for group in groups)
            and 0 < len(groups[0]) <= 3
            and groups[0] != "0"
            and all(len(group) == 3 for group in groups[1:])
        )
        if count > 1:
            if not looks_grouped:
                raise ValueError("inconsistent decimal separators")
        elif not looks_grouped:
            decimal_character = separator

    if decimal_character is None:
        integer, fraction = value, ""
    else:
        integer, fraction_part = value.rsplit(decimal_character, 1)
        if not fraction_part.isdigit():
            raise ValueError("invalid decimal fraction")
        fraction = "." + fraction_part

    grouping_characters = set(integer) - set("0123456789")
    normalized_grouping = {
        " " if character == "\u00a0" else character
        for character in grouping_characters
    }
    if len(normalized_grouping) > 1:
        raise ValueError("inconsistent grouping separators")
    if grouping_characters:
        grouping_character = next(iter(grouping_characters))
        if grouping_character in {" ", "\u00a0"}:
            groups = integer.replace("\u00a0", " ").split(" ")
        else:
            groups = integer.split(grouping_character)
        if (
            not all(group.isdigit() for group in groups)
            or not 0 < len(groups[0]) <= 3
            or any(len(group) != 3 for group in groups[1:])
        ):
            raise ValueError("invalid digit grouping")
        integer = "".join(groups)
    elif not integer.isdigit():
        raise ValueError("invalid decimal integer")

    try:
        return format(Decimal(sign + integer + fraction + exponent), "f")
    except InvalidOperation as exc:
        raise ValueError(f"could not parse {original!r} as a decimal") from exc
