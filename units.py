#!/usr/bin/env python3
"""units — a small command-line unit converter.

Convert a value between units in the same category, without reaching
for a website or a calculator. Pure standard library, no dependencies.

    units convert 5 km mi
    units 5 km to mi
    units 100 C to F
    units list length
    units categories
"""

import sys

__version__ = "0.1.0"


class UnitsError(Exception):
    """A conversion problem the user can fix (unknown unit, wrong pair)."""


# Linear categories are stored as: unit -> (factor to base unit, aliases).
# Temperature is handled separately because it needs an offset, not a factor.
_CATEGORIES = {
    "length": {
        "base": "m",
        "units": {
            "m": (1.0, ["meter", "meters", "metre", "metres"]),
            "km": (1000.0, ["kilometer", "kilometers", "kilometre", "kilometres"]),
            "cm": (0.01, ["centimeter", "centimeters", "centimetre", "centimetres"]),
            "mm": (0.001, ["millimeter", "millimeters", "millimetre", "millimetres"]),
            "mi": (1609.344, ["mile", "miles"]),
            "yd": (0.9144, ["yard", "yards"]),
            "ft": (0.3048, ["foot", "feet"]),
            "in": (0.0254, ["inch", "inches"]),
        },
    },
    "mass": {
        "base": "kg",
        "units": {
            "kg": (1.0, ["kilogram", "kilograms"]),
            "g": (0.001, ["gram", "grams"]),
            "mg": (0.000001, ["milligram", "milligrams"]),
            "lb": (0.45359237, ["lbs", "pound", "pounds"]),
            "oz": (0.028349523125, ["ounce", "ounces"]),
        },
    },
    "volume": {
        "base": "L",
        "units": {
            "L": (1.0, ["l", "liter", "liters", "litre", "litres"]),
            "mL": (0.001, ["ml", "milliliter", "milliliters", "millilitre", "millilitres"]),
            "gal": (3.785411784, ["gallon", "gallons"]),
            "qt": (0.946352946, ["quart", "quarts"]),
            "pt": (0.473176473, ["pint", "pints"]),
            "cup": (0.2365882365, ["cups"]),
            "fl oz": (0.0295735295625, ["floz", "fluid ounce", "fluid ounces"]),
        },
    },
    "area": {
        "base": "sq m",
        "units": {
            "sq m": (1.0, ["m2", "m²", "square meter", "square meters", "square metre", "square metres"]),
            "sq km": (1_000_000.0, ["km2", "km²", "square kilometer", "square kilometers"]),
            "sq ft": (0.09290304, ["ft2", "ft²", "square foot", "square feet"]),
            "sq mi": (2_589_988.110336, ["mi2", "mi²", "square mile", "square miles"]),
            "acre": (4046.8564224, ["acres"]),
            "hectare": (10_000.0, ["ha", "hectares"]),
        },
    },
    "data": {
        "base": "B",
        "units": {
            "B": (1.0, ["byte", "bytes"]),
            "KB": (1000.0, ["kilobyte", "kilobytes"]),
            "MB": (1000.0 ** 2, ["megabyte", "megabytes"]),
            "GB": (1000.0 ** 3, ["gigabyte", "gigabytes"]),
            "TB": (1000.0 ** 4, ["terabyte", "terabytes"]),
            "KiB": (1024.0, ["kibibyte", "kibibytes"]),
            "MiB": (1024.0 ** 2, ["mebibyte", "mebibytes"]),
            "GiB": (1024.0 ** 3, ["gibibyte", "gibibytes"]),
        },
    },
    "speed": {
        "base": "m/s",
        "units": {
            "m/s": (1.0, ["mps", "meter per second", "meters per second"]),
            "km/h": (1.0 / 3.6, ["kph", "kmh", "kilometer per hour", "kilometers per hour"]),
            "mph": (0.44704, ["mile per hour", "miles per hour"]),
            "knot": (0.5144444444444445, ["knots", "kn", "kt"]),
        },
    },
    "time": {
        "base": "s",
        "units": {
            "s": (1.0, ["sec", "secs", "second", "seconds"]),
            "min": (60.0, ["minute", "minutes"]),
            "h": (3600.0, ["hr", "hrs", "hour", "hours"]),
            "day": (86400.0, ["days"]),
            "week": (604800.0, ["weeks"]),
        },
    },
}

# Temperature units and their aliases. Conversion goes through Celsius.
_TEMPERATURE_UNITS = {
    "C": ["celsius", "degc", "°c", "centigrade"],
    "F": ["fahrenheit", "degf", "°f"],
    "K": ["kelvin", "degk"],
}


def _normalize(name):
    """Normalize a unit name for lookup: lowercase, single spaces, trimmed."""
    return " ".join(str(name).strip().lower().split())


def _build_alias_map():
    """Map every normalized alias to (category, canonical unit name)."""
    alias_map = {}
    for category, spec in _CATEGORIES.items():
        for unit, (_factor, aliases) in spec["units"].items():
            alias_map[_normalize(unit)] = (category, unit)
            for alias in aliases:
                alias_map[_normalize(alias)] = (category, unit)
    for unit, aliases in _TEMPERATURE_UNITS.items():
        alias_map[_normalize(unit)] = ("temperature", unit)
        for alias in aliases:
            alias_map[_normalize(alias)] = ("temperature", unit)
    return alias_map


_ALIASES = _build_alias_map()


def categories():
    """Return the list of category names."""
    return list(_CATEGORIES) + ["temperature"]


def units_in(category):
    """Return the canonical unit names of a category, or raise UnitsError."""
    key = _normalize(category)
    if key == "temperature":
        return list(_TEMPERATURE_UNITS)
    for name, spec in _CATEGORIES.items():
        if _normalize(name) == key:
            return list(spec["units"])
    raise UnitsError(f"unknown category: {category!r} "
                     f"(try: {', '.join(categories())})")


def resolve(unit):
    """Resolve a unit name/alias to (category, canonical unit name)."""
    found = _ALIASES.get(_normalize(unit))
    if found is None:
        raise UnitsError(f"unknown unit: {unit!r} "
                         f"(try `units list` to see supported units)")
    return found


def _to_celsius(value, unit):
    if unit == "C":
        return value
    if unit == "F":
        return (value - 32.0) * 5.0 / 9.0
    return value - 273.15  # K


def _from_celsius(value, unit):
    if unit == "C":
        return value
    if unit == "F":
        return value * 9.0 / 5.0 + 32.0
    return value + 273.15  # K


def convert(value, from_unit, to_unit):
    """Convert value from from_unit to to_unit.

    Raises UnitsError for unknown units or units in different categories,
    and ValueError for a non-numeric value.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise UnitsError(f"not a number: {value!r}")
    from_cat, from_name = resolve(from_unit)
    to_cat, to_name = resolve(to_unit)
    if from_cat != to_cat:
        raise UnitsError(
            f"cannot convert {from_name} ({from_cat}) to "
            f"{to_name} ({to_cat}): different categories")
    if from_cat == "temperature":
        if from_name == "K" and number < 0:
            raise UnitsError("temperature below absolute zero: "
                             f"{number} K is not possible")
        result = _from_celsius(_to_celsius(number, from_name), to_name)
        if to_name == "K" and result < 0:
            raise UnitsError("result below absolute zero: "
                             f"{result} K is not possible")
        return result
    from_factor = _CATEGORIES[from_cat]["units"][from_name][0]
    to_factor = _CATEGORIES[to_cat]["units"][to_name][0]
    return number * from_factor / to_factor


def format_number(value):
    """Format a number cleanly: up to 6 decimals, no trailing zeros."""
    if value == 0:
        return "0"
    if abs(value) >= 1e9 or abs(value) < 1e-6:
        return f"{value:.6g}"
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text


def format_result(value, from_unit, to_unit, result):
    """Render a conversion as a single readable line."""
    _, from_name = resolve(from_unit)
    _, to_name = resolve(to_unit)
    return (f"{format_number(float(value))} {from_name} = "
            f"{format_number(result)} {to_name}")


def _split_units(tokens):
    """Split token list into (from_unit, to_unit) trying the longest match.

    Handles multi-word units such as "sq m" and "fl oz": the split point
    that makes both sides known units wins, preferring a longer from-unit.
    """
    first_error = None
    for split in range(len(tokens) - 1, 0, -1):
        from_text = " ".join(tokens[:split])
        to_text = " ".join(tokens[split:])
        try:
            resolve(from_text)
            resolve(to_text)
        except UnitsError as exc:
            if first_error is None:
                first_error = exc
            continue
        return from_text, to_text
    if first_error is not None:
        raise first_error
    raise UnitsError(f"could not parse units from: {' '.join(tokens)!r}")


def _parse_convert_args(args):
    """Parse the tokens after `convert` (or the natural form) into
    (value, from_unit, to_unit). Accepts an optional 'to' keyword."""
    if len(args) < 3:
        raise UnitsError("usage: units convert <value> <from-unit> <to-unit> "
                         "or: units <value> <from-unit> to <to-unit>")
    try:
        value = float(args[0])
    except ValueError:
        raise UnitsError(f"not a number: {args[0]!r}")
    rest = args[1:]
    lowered = [_normalize(t) for t in rest]
    if "to" in lowered:
        idx = lowered.index("to")
        from_text = " ".join(rest[:idx])
        to_text = " ".join(rest[idx + 1:])
        if not from_text or not to_text:
            raise UnitsError("usage: units <value> <from-unit> to <to-unit>")
        return value, from_text, to_text
    return value, *_split_units(rest)


def _print_usage(stream=sys.stderr):
    stream.write(
        "usage:\n"
        "  units convert <value> <from-unit> <to-unit>\n"
        "  units <value> <from-unit> to <to-unit>\n"
        "  units list [category]\n"
        "  units categories\n"
    )


def main(argv=None):
    """CLI entry point. Returns an exit code (0 on success)."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        _print_usage(sys.stdout if args else sys.stderr)
        print("\nConvert a value between units. Examples:\n"
              "  units convert 5 km mi\n"
              "  units 5 km to mi\n"
              "  units 100 C to F\n"
              "  units list length\n"
              "  units categories")
        return 0 if args else 2
    if args[0] in ("-V", "--version"):
        print(f"units {__version__}")
        return 0

    command = _normalize(args[0])
    try:
        if command == "categories":
            for name in categories():
                print(name)
            return 0
        if command == "list":
            if len(args) > 2:
                raise UnitsError("usage: units list [category]")
            if len(args) == 2:
                for unit in units_in(args[1]):
                    print(unit)
            else:
                for name in categories():
                    print(f"{name}: {', '.join(units_in(name))}")
            return 0
        if command == "convert":
            value, from_unit, to_unit = _parse_convert_args(args[1:])
        else:
            value, from_unit, to_unit = _parse_convert_args(args)
    except UnitsError as exc:
        print(f"units: error: {exc}", file=sys.stderr)
        return 1

    try:
        result = convert(value, from_unit, to_unit)
    except UnitsError as exc:
        print(f"units: error: {exc}", file=sys.stderr)
        return 1
    print(format_result(value, from_unit, to_unit, result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
