"""Enum Mixins."""

__author__ = """Maxim Zaslavsky"""
__email__ = "maxim@maximz.com"
__version__ = "0.0.1"

import functools
from typing import List, Iterator, Any
from typing_extensions import Self

import aenum


class IterableFlagMixin:
    """Mixin for aenum.Flag:
    All aenum.Flag values are iterable. This assigns type hints to the iteration variable.
    Note: stdlib Flag doesn't seem to support value iteration.
    TODO: this should just be a type stub file, and not a mixin. Make aenum type stub file based on typeshed stdlib Enum stub?
    """

    @staticmethod
    def combine_flags_list_into_single_multiflag_value(
        lst: List[aenum.Flag],
    ) -> aenum.Flag:
        """Convert a list of individual flags into a single multi-flag instance, by OR-ing all the entries of the list.
        Example: [Test.test, Test.test2] -> Test.test | Test.test2
        Especially useful in a CLI that stores input arguments in a list.
        """
        # TODO: support generics
        return functools.reduce(lambda x, y: x | y, lst)

    def __iter__(self: Self) -> Iterator[Self]:
        return super().__iter__()


class ValidatableEnumMixin:
    """Make your Enum support validate()
    Supports Enum.Flag and AEnum.Flag
    """

    @classmethod
    def validate(cls, key: Any) -> None:
        """Validate that key is a valid enum key."""
        # Type checking
        if not isinstance(key, cls):
            raise TypeError(f"Key must be an instance of the {cls.__name__} enum")


class ValidatableFlagMixin(ValidatableEnumMixin):
    """Make your Flag support validate() (from ValidatableEnumMixin) and validate_single_value()
    Supports Enum.Flag and AEnum.Flag
    """

    @classmethod
    def validate_single_value(cls, key: Any) -> None:
        """Validate that this instance of the flag is only one flag value.
        myflag.A and myflag.B are valid, but (myflag.A | myflag.B) is not.
        (If you defined an enum value C = A | B up-front, then myflag.C will be rejected as well.)
        """
        # First, type check
        cls.validate(key)

        # Now confirm that only one
        if len(key) > 1:
            raise ValueError(f"Must specify only one {cls.__name__} value; got {key}")


class NonNullableFlagMixin:
    """Flag Enum that does not allow null/0 values.
    Requires aenum.Flag rather than enum.Flag.
    """

    # TODO: cleaner approach by subclassing EnumMeta metaclass? see https://stackoverflow.com/a/32313954/130164
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 0 in self._value2member_map_.keys():
            raise ValueError(
                f"Can't initialize NotNullableFlag {self.__name__} enum with a null zero value."
            )

    @classmethod
    def _missing_value_(cls, value: Any) -> Any:
        result = super()._missing_value_(value)
        if result.value == 0:
            # remove so that it's still considered a missing value in the future
            del cls._value2member_map_[0]
            # raise error
            raise ValueError(
                f"Null / zero-value is not allowed in NotNullableFlag {cls.__name__} enum."
            )
        return result


class CustomNameSeparatorFlagMixin:
    """Flag Enum that allows custom name separator for multi values.
    Set default by including: `__default_separator__ = "_"`
    Default to `|`.

    Note that Python built-in Enum doesn't support .name for flags with multiple values, so we use aenum.Flag instead:
    see https://stackoverflow.com/a/60799487/130164 and https://bugs.python.org/issue40042 and https://bugs.python.org/issue38250 - fixed in Python 3.10?
    """

    __default_separator__ = "|"

    @property
    def name(self) -> str:
        super_name = super().name
        if isinstance(super_name, str):
            return super_name.replace("|", self.__default_separator__)
        return super_name
