# Enum Mixins

`enum_mixins` is a small Python package of mixins for adding practical behavior
to enum and flag classes, especially `aenum.Flag`.

The package is pre-alpha and intentionally narrow: it provides runtime
validation helpers, type-friendly flag iteration, non-null flag behavior, and
custom names for combined flag values.

## What It Provides

- `IterableFlagMixin`: keeps `aenum.Flag` values iterable while giving the
  iterator a useful type hint, and includes a helper for OR-ing a non-empty list
  of flags into one combined flag value.
- `ValidatableEnumMixin`: adds `validate(key)`, which accepts only values that
  are instances of the enum class.
- `ValidatableFlagMixin`: adds `validate_single_value(key)`, which rejects
  combined flag values such as `Color.RED | Color.BLUE`.
- `NonNullableFlagMixin`: rejects zero/null `aenum.Flag` values produced at
  runtime, such as `Color(0)` or operations whose result is zero.
- `CustomNameSeparatorFlagMixin`: customizes the separator used in generated
  names for combined `aenum.Flag` values, for example `RED_BLUE` instead of
  `RED|BLUE`.

## Installation

```bash
pip install enum_mixins
```

The package requires Python 3.8 or newer and depends on `aenum` and
`typing-extensions`.

For local development:

```bash
pip install -r requirements_dev.txt
pip install -e .
make test
make lint
```

## Usage

Place mixins before `aenum.Flag` in the class bases:

```python
import aenum
from enum_mixins import (
    CustomNameSeparatorFlagMixin,
    IterableFlagMixin,
    NonNullableFlagMixin,
    ValidatableFlagMixin,
)


class Color(
    IterableFlagMixin,
    ValidatableFlagMixin,
    NonNullableFlagMixin,
    CustomNameSeparatorFlagMixin,
    aenum.Flag,
):
    __default_separator__ = "_"

    RED = aenum.auto()
    BLUE = aenum.auto()
    GREEN = aenum.auto()
    MIXED = RED | GREEN


Color.validate(Color.RED)
Color.validate(Color.RED | Color.BLUE)

Color.validate_single_value(Color.RED)
# Color.validate_single_value(Color.RED | Color.BLUE) raises ValueError

(Color.RED | Color.BLUE).name
# "RED_BLUE"

list(Color.RED | Color.BLUE)
# [Color.RED, Color.BLUE]

Color(0)
# raises ValueError
```

`CustomNameSeparatorFlagMixin` only changes generated combined names. If a
combined value is explicitly named in the enum, such as `MIXED = RED | GREEN`,
the defined enum name is preserved.

## Behavior Notes

The validation mixins work at runtime: `validate()` checks that the value is an
instance of the enum class, and `validate_single_value()` additionally checks
that exactly one flag is set. They do not parse strings or coerce external
values into enum members.

`NonNullableFlagMixin` is intended for `aenum.Flag`. The current tests cover
runtime zero-value rejection, but class-definition-time rejection of an explicit
zero member is marked as expected-fail.

`IterableFlagMixin.combine_flags_list_into_single_multiflag_value()` uses
`functools.reduce`, so it expects at least one flag in the list.

## Project Status

Version `0.0.1` is marked as pre-alpha in the package metadata. The project is
MIT licensed.
