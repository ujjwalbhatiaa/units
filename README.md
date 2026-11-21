# units

A small command-line unit converter. Convert a value between units in the
same category — length, mass, temperature, volume, area, data, speed, time —
without reaching for a website or a calculator.

Pure Python standard library. No dependencies, no setup beyond Python 3.8+.

## Usage

```sh
python3 units.py convert 5 km mi
python3 units.py 5 km to mi
python3 units.py 100 C to F
python3 units.py list length
python3 units.py categories
```

Both the `convert` subcommand and the natural form work, with or without
the word `to`:

```
$ python3 units.py convert 5 km mi
5 km = 3.106856 mi

$ python3 units.py 100 C to F
100 C = 212 F

$ python3 units.py 2 GiB MiB
2 GiB = 2048 MiB

$ python3 units.py 1 sq m to sq ft
1 sq m = 10.76391 sq ft
```

Make it directly runnable if you like:

```sh
chmod +x units.py
./units.py 60 mph to km/h
```

## Supported units

Unit names are case-insensitive, and most have everyday aliases
(`feet`, `pounds`, `celsius`, `floz`, ...). Multi-word units such as
`sq m` and `fl oz` work in the natural form.

| Category    | Units |
| ----------- | ----- |
| length      | m, km, cm, mm, mi, yd, ft, in |
| mass        | kg, g, mg, lb, oz |
| temperature | C, F, K |
| volume      | L, mL, gal, qt, pt, cup, fl oz |
| area        | sq m, sq km, sq ft, sq mi, acre, hectare |
| data        | B, KB, MB, GB, TB, KiB, MiB, GiB |
| speed       | m/s, km/h, mph, knot |
| time        | s, min, h, day, week |

Temperature uses the real offset formulas (C ↔ F ↔ K), not a scale factor.
Data sizes keep decimal and binary apart on purpose: `KB` is 1000 bytes,
`KiB` is 1024.

Run `units list [category]` to see the units in one category, or
`units list` for all of them. `units categories` lists the categories.

## Errors

Mistakes fail loudly with a clear message and a non-zero exit code:

```
$ python3 units.py 5 km to kg
units: error: cannot convert km (length) to kg (mass): different categories

$ python3 units.py convert 5 furlong m
units: error: unknown unit: 'furlong' (try `units list` to see supported units)

$ python3 units.py convert abc km mi
units: error: not a number: 'abc'
```

## Tests

```sh
python3 -m pytest tests/ -q
```

58 tests cover every category, temperature offsets, aliases, multi-word
units, error paths, and CLI exit codes.

## License

MIT — see [LICENSE](LICENSE).
