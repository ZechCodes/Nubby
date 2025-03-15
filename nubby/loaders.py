from abc import ABC, abstractmethod
from functools import wraps
from pathlib import Path
from typing import Any, Callable, overload


class ConfigLoader(ABC):
    extensions: set[str]

    def __init__(self, path: Path):
        self._path = path

    @overload
    def load(self) -> dict[str, Any]:
        ...

    @overload
    def load(self, key: str) -> dict[str, Any]:
        ...

    @overload
    def load(self, key: str, default: Any) -> dict[str, Any] | Any:
        ...

    @abstractmethod
    def load(self, *args) -> dict[str, Any]:
        """Loads data from a file and returns it as a dictionary. If a key is provided, the data under that key is
        returned. An optional default can be provided with the key if the key doesn't exist in the config. This data may
        be cached for future use, so this function does not always have to result in IO operations."""
        ...

    @abstractmethod
    def write(self, data: dict[str, Any]):
        """Writes data to a file overwriting the existing data and updating any in memory cache."""
        ...

    @classmethod
    @abstractmethod
    def supported(cls) -> bool:
        """Returns True if the handler can be used in the current environment. For example, a handler would return False
        if a required parser library is not installed."""
        ...


def ensure_supported[F: Callable](message: str) -> Callable[[F], F]:
    def wrap(func: F) -> F:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.supported():
                raise ImportError(message)

            return func(self, *args, **kwargs)

        return wrapper

    return wrap