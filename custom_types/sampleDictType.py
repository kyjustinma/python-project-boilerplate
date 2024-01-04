from typing import TypedDict


# Types should be PascalCase
class NestedDictType(TypedDict):
    test: str
    nested: str


class SampleDictType(TypedDict):
    string: str
    integer: int
    float: float
    boolean: bool
    list: list
    dictionary: NestedDictType


class DotDict(dict):
    """allows for dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Variables have all lowercase + underscores
sample_dict: SampleDictType = {}
sample_dict["string"] = "hello"
# Returns suggestive keys

new_sample_dict = DotDict(sample_dict)
