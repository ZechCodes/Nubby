from tramp.optionals import Optional
from typing import Any

try:
    import tomlkit as toml
except ImportError:
    try:
        import tomllib as toml
    except ImportError:
        toml = None

from nubby.loaders import ConfigLoader, ensure_supported


class TomlLoader(ConfigLoader):
    extensions = {"toml"}

    @ensure_supported("tomllib or tomlkit are required to use TOML files.")
    def __init__(self, path):
        super().__init__(path)
        self._data: Optional[dict[str, Any]] = Optional.Nothing()

    def load(self, *args) -> dict[str, Any]:
        match args:
            case [str() as key, default]:
                return self._load().get(key, default)

            case [str() as key]:
                return self._load()[key]

            case []:
                return self._load()

            case _:
                raise ValueError(f"Expected no arguments or a key to load, got {args}")

    def write(self, data: dict[str, Any]):
        if hasattr(toml, "dumps"):
            with self._path.open("w") as file:
                file.write(toml.dumps(data))
                self._data = Optional.Some(data)

        raise ImportError(
            "tomlkit is required to write TOML files."
        )

    def _load(self) -> dict[str, Any]:
        match self._data:
            case Optional.Some(data):
                return data

            case Optional.Nothing():
                self._data = Optional.Some(self._load_file())
                return self._data.value

            case _:
                raise ValueError(f"Unexpected value for self._data: {self._data}")

    def _load_file(self) -> dict[str, Any]:
        with self._path.open("r") as file:
            return toml.loads(file.read())

    @classmethod
    def supported(cls) -> bool:
        return toml is not None
