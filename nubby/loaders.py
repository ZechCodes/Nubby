"""This module provides the ConfigLoader interface for loader types that load and write to config files.

Loaders are instantiated with a path to the config file. The loader is responsible for loading the data from the file and
caching it for future use. The loader is also responsible for writing the data back to the file. The loader instance
is stored in the config controller and reused for populating models in the future.

Each loader should provide a set of file extensions that it supports. The config controller will use this to determine
which loader to use for a given file.

Loaders should provide a supported() classmethod if they require optional package dependencies. If the dependencies are
not installed, the loader's supported() method should return False.
"""
from abc import ABC, abstractmethod
from functools import wraps
from pathlib import Path
from typing import Any, Callable, overload


class ConfigLoader(ABC):
    """Abstract base class for config file loaders. Each loader must provide a set of file extensions that it supports.

    A new instance of the loader is created for each config file that is loaded. This instance is stored in the config
    controller and reused for populating models in the future.

    Loaders can and probably should cache the config data for these future populates, it is not enforced by the
    interface though.
    """
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
    def supported(cls) -> bool:
        """Returns True if the handler can be used in the current environment. For example, a handler would return False
        if a required parser library is not installed."""
        return True


def ensure_supported[F: Callable](message: str) -> Callable[[F], F]:
    """Decorator that raises an ImportError if the loader is not supported. This should be used for optional loaders
    that have package dependencies that may not be installed. The loader should implement the supported() classmethod
    and it should return False if the loader is not supported in the current environment.

    This is used by the toml and yaml loaders on their init methods to ensure the required packages are installed
    when loaders are instantiated."""
    def wrap(func: F) -> F:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.supported():
                raise ImportError(message)

            return func(self, *args, **kwargs)

        return wrapper

    return wrap