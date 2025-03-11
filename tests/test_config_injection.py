from dataclasses import dataclass
from pathlib import Path

from nubby import ConfigController, ConfigModel
from nubby.controllers import ConfigFile, set_active_controller

from bevy import get_registry, get_container, inject, dependency
from bevy.registries import Registry

from nubby.models import model_injector


@dataclass
class Model(ConfigModel):
    __config_filename__ = "testing_config"

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
