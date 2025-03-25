from dataclasses import dataclass
from pathlib import Path

from nubby import model_injector, new_file_model
from nubby.controllers import ConfigController, set_active_controller
from nubby.loaders import ConfigLoader

from bevy import get_container, inject, dependency
from bevy.registries import Registry


file_definition = new_file_model("testing_config")

@file_definition.section("test_model")
@dataclass
class Model:
    foo: str
    bar: int


class MockConfigController(ConfigController):
    def __init__(self, **loaded_configs: ConfigLoader):
        super().__init__()
        self._loaded_configs = loaded_configs

    def _get_config_file(self, filename: str) -> ConfigLoader:
        return self._loaded_configs[filename]


class MockLoader(ConfigLoader):
    def __init__(self, path):
        super().__init__(path)
        self.data = None

    def load(self, key: str = "") -> dict:
        if key == "":
            return self.data

        return self.data[key]

    def set_test_data(self, data):
        self.data = data
        return self

    def write(self, data: dict):
        self.data = data

    @classmethod
    def supported(cls) -> bool:
        return True


def test_injection():
    controller = MockConfigController(
        testing_config=MockLoader(Path("/testing_config.json")).set_test_data({"test_model": {"foo": "baz", "bar": 42}})
    )
    registry = Registry()
    registry.add_hook(model_injector)
    container = get_container(using_registry=registry)
    set_active_controller(controller, container)

    @inject
    def testing(model: Model = dependency()):
        return model

    m = container.call(testing)
    assert m.foo == "baz"
    assert m.bar == 42
