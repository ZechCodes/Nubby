from dataclasses import dataclass
from pathlib import Path

from nubby.controllers import ConfigController
from nubby import new_file_model
from io import StringIO


json_file = new_file_model("example_json")

@json_file.section("data")
@dataclass
class JsonModel:
    key: str


toml_file = new_file_model("example_toml")

@toml_file.section("data")
@dataclass
class TomlModel:
    name: str


class UnclosableIO(StringIO):
    def close(self):
        self.seek(0)


class DummyPath(Path):
    files = {
        "/example_json.json": UnclosableIO('{"data": {"key": "value"}}'),
        "/example_toml.toml": UnclosableIO('[data]\nname = "bob"'),
    }
    def __truediv__(self, other):
        return DummyPath(super().__truediv__(other))

    def is_file(self):
        return "." in str(self)

    def exists(self):
        return str(self) in self.files

    def open(self, mode):
        if str(self) not in self.files:
            raise RuntimeError(f"Not a file: {self}")

        if mode == "wb":
            self.files[str(self)].truncate(0)

        return self.files[str(self)]

    @classmethod
    def cwd(cls):
        return cls("/")


def test_config_loading():
    manager = ConfigController()
    manager.add_path(DummyPath.cwd())
    model = manager.load_config_for(JsonModel)
    assert model.key == "value"

    model = manager.load_config_for(TomlModel)
    assert model.name == "bob"


def test_config_writing():
    manager = ConfigController()
    manager.add_path(DummyPath.cwd())
    change_model = JsonModel("new_value")
    manager.save(change_model)
    model = manager.load_config_for(JsonModel)
    assert model.key == "new_value"
