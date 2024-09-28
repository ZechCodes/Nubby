import json

from nubby import ConfigModel, ConfigController
from io import BytesIO


class JsonModel(ConfigModel, filename="example_json"):
    key: str

    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"key": self.key}


class TomlModel(ConfigModel, filename="example_toml", key="data"):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {"name": self.name}


class UnclosableBytesIO(BytesIO):
    def close(self):
        self.seek(0)


class DummyPath:
    files = {
        "/example_json.json": UnclosableBytesIO(b'{"key": "value"}'),
        "/example_toml.toml": UnclosableBytesIO(b'[data]\nname = "bob"'),
    }
    def __init__(self, path):
        self.path = path

    def __truediv__(self, other):
        return DummyPath(f"{self.path}/{other}")

    def is_file(self):
        return "." in self.path

    def exists(self):
        return self.path in self.files

    def open(self, mode):
        if self.path not in self.files:
            raise RuntimeError(f"Not a file: {self.path}")

        if mode == "wb":
            self.files[self.path].truncate(0)

        return self.files[self.path]

    @classmethod
    def cwd(cls):
        return cls("")



def test_config_loading():
    manager = ConfigController([DummyPath.cwd()])
    model = manager.load_config_for(JsonModel)
    assert model.key == "value"

    model = manager.load_config_for(TomlModel)
    assert model.name == "bob"


def test_config_writing():
    manager = ConfigController([DummyPath.cwd()])
    change_model = JsonModel("new_value")
    manager.save(change_model)
    model = manager.load_config_for(JsonModel)
    assert model.key == "new_value"
