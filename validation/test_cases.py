from dataclasses import dataclass
from typing import List


@dataclass
class TestCase:
    __test__ = False
    input_string: str
    expected: bool
    description: str = ""
