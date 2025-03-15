from pathlib import Path
from tramp.optionals import Optional
from typing import Any

try:
    import yaml

except ImportError:
    yaml = None

from nubby.loaders import ConfigLoader, ensure_supported


class YamlLoader(ConfigLoader):
    extensions = {"yaml", "yml"}

    @ensure_supported("pyyaml is required to use YAML files.")
    def __init__(self, path: Path):
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
        with self._path.open("w") as f:
            yaml.safe_dump(data, f)
            self._data = Optional.Some(data)

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
        with self._path.open("r") as f:
            return yaml.safe_load(f)

    @classmethod
    def supported(cls) -> bool:
        return yaml is not None
