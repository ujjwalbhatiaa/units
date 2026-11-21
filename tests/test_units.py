"""Tests for units — the command-line unit converter."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from units import (  # noqa: E402
    UnitsError,
    categories,
    convert,
    format_number,
    format_result,
    resolve,
    units_in,
    main,
)

UNITS_PY = Path(__file__).resolve().parent.parent / "units.py"


# --- length ---

def test_length_km_to_mi():
    assert convert(5, "km", "mi") == pytest.approx(3.106855, abs=1e-6)


def test_length_mi_to_km():
    assert convert(1, "mi", "km") == pytest.approx(1.609344)


def test_length_m_to_ft():
    assert convert(1, "m", "ft") == pytest.approx(3.280839895, abs=1e-6)


def test_length_cm_to_in():
    assert convert(2.54, "cm", "in") == pytest.approx(1.0)


def test_length_yd_to_m():
    assert convert(3, "yd", "m") == pytest.approx(2.7432)


def test_length_same_unit_is_identity():
    assert convert(42, "km", "km") == 42


def test_length_aliases():
    assert convert(1, "mile", "km") == pytest.approx(1.609344)
    assert convert(1, "foot", "m") == pytest.approx(0.3048)
    assert convert(1, "meters", "cm") == pytest.approx(100.0)
    assert convert(1, "inches", "mm") == pytest.approx(25.4)


def test_units_are_case_insensitive():
    assert convert(1, "KM", "MI") == pytest.approx(0.6213711922, abs=1e-9)
    assert convert(100, "c", "f") == pytest.approx(212.0)


# --- mass ---

def test_mass_kg_to_lb():
    assert convert(1, "kg", "lb") == pytest.approx(2.2046226218, abs=1e-6)


def test_mass_lb_to_oz():
    assert convert(1, "lb", "oz") == pytest.approx(16.0)


def test_mass_g_to_mg():
    assert convert(1, "g", "mg") == pytest.approx(1000.0)


def test_mass_alias_pounds():
    assert convert(2, "pounds", "kg") == pytest.approx(0.90718474)


# --- temperature (offsets, not factors) ---

def test_temp_c_to_f_boiling():
    assert convert(100, "C", "F") == pytest.approx(212.0)


def test_temp_c_to_f_freezing():
    assert convert(0, "C", "F") == pytest.approx(32.0)


def test_temp_f_to_c():
    assert convert(32, "F", "C") == pytest.approx(0.0)
    assert convert(98.6, "F", "C") == pytest.approx(37.0)


def test_temp_c_to_k():
    assert convert(0, "C", "K") == pytest.approx(273.15)
    assert convert(-273.15, "C", "K") == pytest.approx(0.0)


def test_temp_k_to_f():
    assert convert(273.15, "K", "F") == pytest.approx(32.0)


def test_temp_minus_40_is_same():
    assert convert(-40, "C", "F") == pytest.approx(-40.0)


def test_temp_negative_kelvin_rejected():
    with pytest.raises(UnitsError, match="absolute zero"):
        convert(-1, "K", "C")


def test_temp_aliases():
    assert convert(0, "celsius", "fahrenheit") == pytest.approx(32.0)
    assert convert(273.15, "kelvin", "C") == pytest.approx(0.0)


# --- volume ---

def test_volume_l_to_ml():
    assert convert(1, "L", "mL") == pytest.approx(1000.0)


def test_volume_gal_to_l():
    assert convert(1, "gal", "L") == pytest.approx(3.785411784)


def test_volume_cup_to_ml():
    assert convert(1, "cup", "mL") == pytest.approx(236.5882365)


def test_volume_fl_oz_multiword():
    assert convert(1, "fl oz", "mL") == pytest.approx(29.5735295625)
    assert convert(8, "floz", "cup") == pytest.approx(1.0)


# --- area ---

def test_area_sq_m_to_sq_ft():
    assert convert(1, "sq m", "sq ft") == pytest.approx(10.7639104167, abs=1e-6)


def test_area_acre_to_sq_m():
    assert convert(1, "acre", "sq m") == pytest.approx(4046.8564224)


def test_area_hectare_alias():
    assert convert(1, "ha", "sq m") == pytest.approx(10_000.0)
    assert convert(1, "hectare", "acre") == pytest.approx(2.4710538147, abs=1e-6)


# --- data ---

def test_data_decimal_vs_binary():
    assert convert(1, "KB", "B") == pytest.approx(1000.0)
    assert convert(1, "KiB", "B") == pytest.approx(1024.0)
    assert convert(1, "MB", "KB") == pytest.approx(1000.0)
    assert convert(1, "MiB", "KiB") == pytest.approx(1024.0)


def test_data_gb_to_mb():
    assert convert(2, "GB", "MB") == pytest.approx(2000.0)


# --- speed ---

def test_speed_kmh_to_ms():
    assert convert(36, "km/h", "m/s") == pytest.approx(10.0)


def test_speed_mph_to_kmh():
    assert convert(60, "mph", "km/h") == pytest.approx(96.56064)


def test_speed_knot_alias():
    assert convert(1, "knots", "km/h") == pytest.approx(1.852, abs=1e-3)


# --- time ---

def test_time_day_to_hours():
    assert convert(1, "day", "h") == pytest.approx(24.0)


def test_time_week_to_min():
    assert convert(1, "week", "min") == pytest.approx(10_080.0)


def test_time_aliases():
    assert convert(90, "secs", "min") == pytest.approx(1.5)
    assert convert(2, "hrs", "min") == pytest.approx(120.0)


# --- errors ---

def test_unknown_unit():
    with pytest.raises(UnitsError, match="unknown unit"):
        convert(1, "furlong", "m")


def test_mismatched_categories():
    with pytest.raises(UnitsError, match="different categories"):
        convert(5, "km", "kg")


def test_mismatched_temperature_vs_length():
    with pytest.raises(UnitsError, match="different categories"):
        convert(5, "C", "m")


def test_bad_number():
    with pytest.raises(UnitsError, match="not a number"):
        convert("abc", "km", "mi")


def test_unknown_category():
    with pytest.raises(UnitsError, match="unknown category"):
        units_in("pressure")


# --- lookup helpers ---

def test_categories_lists_all_eight():
    cats = categories()
    assert cats == ["length", "mass", "volume", "area",
                    "data", "speed", "time", "temperature"]


def test_units_in_length():
    assert units_in("length") == ["m", "km", "cm", "mm", "mi", "yd", "ft", "in"]


def test_resolve_alias_returns_canonical():
    assert resolve("feet") == ("length", "ft")
    assert resolve("F") == ("temperature", "F")


def test_format_number_trims_zeros():
    assert format_number(3.106855961) == "3.106856"
    assert format_number(100.0) == "100"
    assert format_number(0) == "0"


def test_format_result_line():
    assert format_result(5, "km", "mi", 3.106855) == "5 km = 3.106855 mi"


# --- CLI ---

def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(UNITS_PY), *args],
        capture_output=True, text=True)


def test_cli_convert_subcommand():
    proc = run_cli("convert", "5", "km", "mi")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "5 km = 3.106856 mi"


def test_cli_natural_form_with_to():
    proc = run_cli("5", "km", "to", "mi")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "5 km = 3.106856 mi"


def test_cli_natural_form_without_to():
    proc = run_cli("100", "C", "F")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "100 C = 212 F"


def test_cli_multiword_units():
    proc = run_cli("1", "sq", "m", "to", "sq", "ft")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "1 sq m = 10.76391 sq ft"


def test_cli_data_conversion():
    proc = run_cli("convert", "2", "GiB", "MiB")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "2 GiB = 2048 MiB"


def test_cli_categories():
    proc = run_cli("categories")
    assert proc.returncode == 0
    assert "temperature" in proc.stdout.splitlines()
    assert len(proc.stdout.splitlines()) == 8


def test_cli_list_category():
    proc = run_cli("list", "length")
    assert proc.returncode == 0
    assert proc.stdout.splitlines() == ["m", "km", "cm", "mm", "mi", "yd", "ft", "in"]


def test_cli_list_all():
    proc = run_cli("list")
    assert proc.returncode == 0
    assert "length: m, km, cm, mm, mi, yd, ft, in" in proc.stdout


def test_cli_unknown_unit_exits_nonzero():
    proc = run_cli("convert", "5", "furlong", "m")
    assert proc.returncode != 0
    assert "unknown unit" in proc.stderr


def test_cli_mismatched_categories_exits_nonzero():
    proc = run_cli("5", "km", "to", "kg")
    assert proc.returncode != 0
    assert "different categories" in proc.stderr


def test_cli_bad_number_exits_nonzero():
    proc = run_cli("convert", "abc", "km", "mi")
    assert proc.returncode != 0
    assert "not a number" in proc.stderr


def test_cli_no_args_exits_nonzero():
    proc = run_cli()
    assert proc.returncode != 0


def test_cli_version():
    proc = run_cli("--version")
    assert proc.returncode == 0
    assert proc.stdout.strip().startswith("units ")
