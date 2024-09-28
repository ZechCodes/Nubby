from typing import Any, overload, Protocol, runtime_checkable, BinaryIO


@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]:
        ...


@runtime_checkable
class ConfigHandler(Protocol):
    extensions: set[str]

    def load(self, file: BinaryIO) -> dict[str, Any]:
        ...

    @overload
    def write(self, data: dict[str, Any], file: BinaryIO):
        ...

    @overload
    def write(self, data: Serializable, file: BinaryIO):
        ...

    def write(self, data: dict | Serializable, file: BinaryIO):
        ...

    @classmethod
    def supported(cls) -> bool:
        ...
