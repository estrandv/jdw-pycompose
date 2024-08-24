"""
This type stub file was generated by pyright.
"""

from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from shuttle_notation.parsing.element import Element

"""

    Parsing related to single-element string-parts.

"""
@dataclass
class ElementInformation:
    prefix: str = ...
    index_string: str = ...
    suffix: str = ...
    repetition: int = ...
    arg_source: str = ...


class InformationPart(Enum):
    PREFIX = ...
    INDEX = ...
    SUFFIX = ...
    REPETITION = ...
    ARGS = ...


def divide_information(element: Element) -> ElementInformation:
    ...

@dataclass
class DynamicArg:
    value: Decimal
    operator: str = ...


def parse_args(arg_source, aliases: dict = ...) -> dict:
    ...
