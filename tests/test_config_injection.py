from dataclasses import dataclass
from pathlib import Path

from nubby import ConfigController, SectionModel
from nubby.controllers import ConfigFile, set_active_controller

from bevy import get_registry, get_container, inject, dependency
from bevy.registries import Registry

from nubby.models import model_injector, new_file_model

file_definition = new_file_model("testing_config")

@file_definition.section
@dataclass
class Model:
    foo: str
    bar: int


class MockConfigController(ConfigController):
    def __init__(self, **config_files: ConfigFile):
        super().__init__()
        self._config_cache = config_files

    def _get_config_file_with_cache(self, filename: str) -> ConfigFile:
        return self._config_cache[filename]


def test_injection():
    controller = MockConfigController(
        testing_config=ConfigFile(
            {"foo": "baz", "bar": 42},
            None,
            Path("/testing_config.json"),
        )
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
