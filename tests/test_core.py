import pytest
import aenum
import enum_mixins


@pytest.mark.xfail
def test_non_nullable_aenum_flag_does_not_allow_null_at_init_time():
    class WrongColorAenumVersion(enum_mixins.NonNullableFlagMixin, aenum.Flag):
        NONE = 0
        RED = aenum.auto()
        BLUE = aenum.auto()

    pass


class Color(
    enum_mixins.IterableFlagMixin,
    enum_mixins.ValidatableFlagMixin,
    enum_mixins.NonNullableFlagMixin,
    enum_mixins.CustomNameSeparatorFlagMixin,
    aenum.Flag,
):
    __default_separator__ = "_"
    RED = aenum.auto()
    BLUE = aenum.auto()
    GREEN = aenum.auto()
    MIXED = RED | GREEN


def test_non_nullable_flag():
    # Test these together. Want to make sure that behavior does not change on second access of 0 element.
    with pytest.raises(ValueError):
        Color(0)
    with pytest.raises(ValueError):
        # Inversion
        ~(Color.BLUE | Color.RED | Color.GREEN)
    with pytest.raises(ValueError):
        # AND
        (Color.BLUE & Color.RED)


def test_custom_name_separator():
    assert Color.RED.name == "RED"
    assert Color.MIXED.name == "MIXED"

    # Order should not matter, and XOR and OR should give same value
    assert (
        (Color.BLUE ^ Color.RED)
        == (Color.RED ^ Color.BLUE)
        == (Color.BLUE | Color.RED)
        == (Color.RED | Color.BLUE)
    )
    assert (
        Color.MIXED
        == Color.RED | Color.GREEN
        == Color.GREEN | Color.RED
        == Color.GREEN ^ Color.RED
        == Color.RED ^ Color.GREEN
    )

    # Name should be same regardless of order
    assert (
        (Color.BLUE ^ Color.RED).name
        == (Color.RED ^ Color.BLUE).name
        == (Color.BLUE | Color.RED).name
        == (Color.RED | Color.BLUE).name
        == "RED_BLUE"
    )

    # Combinations should use set names if available
    assert (
        (Color.GREEN ^ Color.RED).name
        == (Color.RED ^ Color.GREEN).name
        == (Color.GREEN | Color.RED).name
        == (Color.RED | Color.GREEN).name
        == "MIXED"
        != "RED_GREEN"
    )

    # Can check memberships like this:
    assert len(Color.RED | Color.BLUE) == 2
    assert Color.BLUE in (Color.RED | Color.BLUE)
    assert Color.RED in (Color.RED | Color.BLUE)
    assert Color.RED in Color.MIXED
    assert Color.BLUE not in Color.MIXED
    assert (Color.RED | Color.BLUE) not in Color.RED
    assert Color.RED in (Color.RED | Color.BLUE)
    assert (Color.RED | Color.BLUE) in (Color.RED | Color.BLUE)
    assert (Color.RED | Color.BLUE) in (Color.RED | Color.BLUE | Color.GREEN)


def test_validation():
    Color.validate(Color.RED)
    Color.validate(Color.RED | Color.BLUE)
    Color.validate(Color.MIXED)
    with pytest.raises(TypeError):
        Color.validate("RED")
    with pytest.raises(TypeError):
        Color.validate("wrong")


def test_validation_single_value():
    Color.validate_single_value(Color.RED)
    Color.validate_single_value(Color.BLUE)
    with pytest.raises(ValueError):
        Color.validate_single_value(Color.RED | Color.BLUE)
    with pytest.raises(ValueError):
        Color.validate_single_value(Color.MIXED)
    with pytest.raises(ValueError):
        Color.validate_single_value(Color.RED | Color.GREEN)


def test_flag_iterable_even_if_single_value():
    """confirm that aenum Flags are iterable (and not broken by type hint mixin).
    not true for stdlib."""
    # expected to be iterable
    both = Color.RED | Color.BLUE
    assert len(both) == 2
    for flag in both:
        assert flag == Color.RED or flag == Color.BLUE

    # confirm this is still iterable, even though single value
    single = Color.RED
    assert len(single) == 1
    for flag in single:
        assert flag == Color.RED

    # Interesting property of iterating over the enum class:
    # Combined values like `MIXED=RED|GREEN` defined in the class don't count towards the length of the enum!
    assert len(list(Color)) == 3
    assert Color.MIXED not in list(Color)

    # But if we iterate over multi-flag packed values, the components of defined-as-combined values are counted separately
    assert len(Color.BLUE | Color.MIXED) == 3  # counts RED,GREEN,BLUE
    assert len(Color.RED | Color.GREEN) == 2  # counts RED,GREEN
    assert len(Color.MIXED) == 2  # counts RED,GREEN
    assert len(Color.RED | Color.MIXED) == 2  # counts RED,GREEN
    assert (
        len(Color.RED | Color.GREEN | Color.MIXED) == 2
    )  # counts RED,GREEN - mixed already includes both
