from typing import NewType, Union


SafeString = NewType('SafeString', str)


def mark_safe(s: Union[str, SafeString]) -> SafeString:
    ...
