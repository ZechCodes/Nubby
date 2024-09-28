from pathlib import Path
from typing import TypeVar, Type, Iterable, Generator

import bevy

from nubby.handlers import ConfigHandler
import nubby.models

TModel = TypeVar("TModel", bound="nubby.models.Model")

class ConfigFile:
    def __init__(self, data: dict[str, dict], handler: ConfigHandler, path: Path):
        self.data = data
        self.handler = handler
        self.path = path


class ConfigController:
    def __init__(self, paths: Iterable[Path] = (), handlers: Iterable[Type[ConfigHandler]] = ()):
        self._paths = self._setup_paths(paths)
        self._handlers = self._setup_handlers(handlers)
        self._config_cache: dict[str, ConfigFile] = {}

    def add_path(self, path: Path):
        self._paths.append(path)

    def add_handler(self, handler: Type[ConfigHandler]):
        self._handlers.update(self._associate_extensions_to_handlers([handler]))

    def load_config_for(self, model: Type[TModel]) -> TModel:
        filename = model.__config_filename__
        config = self._get_cached_config_file(filename)
        data = config.data
        if model.__config_key__:
            data = data.get(model.__config_key__)
            if data is None:
                raise KeyError(
                    f"Config key {model.__config_key__!r} for {model.__module__}.{model.__qualname__} not found in "
                    f"{filename!r}"
                )

        return model(**data)

    def save(self, model: TModel):
        filename = model.__config_filename__
        config = self._get_cached_config_file(filename)
        if model.__config_key__:
            config.data[model.__config_key__] = model.to_dict()

        else:
            config.data = model.to_dict()

        with config.path.open("wb") as file:
            config.handler.write(config.data, file)

    def _find_config_file(self, filename: str) -> tuple[Path, ConfigHandler]:
        for path in self._paths:
            for extension, handler in self._handlers.items():
                file_path = path / f"{filename}.{extension}"
                if file_path.exists():
                    return file_path, handler

        raise FileNotFoundError(
            f"Config file {filename!r} not found in paths:\n"
            f"{'\n'.join(f'    - {path}' for path in self._paths)}"
        )

    def _get_cached_config_file(self, filename: str) -> ConfigFile:
        file_path, handler = self._find_config_file(filename)
        if file_path not in self._config_cache:
            with file_path.open("rb") as file:
                self._config_cache[filename] = ConfigFile(handler.load(file), handler, file_path)

        return self._config_cache[filename]

    def _setup_paths(self, paths: Iterable[Path]) -> list[Path]:
        path_list = list(paths)

        if not path_list:
            return [Path.cwd()]

        if invalid_paths := [path for path in path_list if path.is_file()]:
            raise ValueError(
                f"Paths must be directories, not files:\n"
                f"{'\n'.join(f'    - {path}' for path in invalid_paths)}"
            )

        return path_list

    def _setup_handlers(self, handlers: Iterable[Type[ConfigHandler]]) -> dict[str, ConfigHandler]:
        handler_list = list(handlers)

        if not handler_list:
            from nubby import JsonHandler, YamlHandler, TomlHandler
            handler_list = [
                handler
                for handler in [JsonHandler, TomlHandler, YamlHandler]
                if handler.supported()
            ]

        elif invalid_handlers := [handler for handler in handler_list if not handler.supported()]:
            raise ValueError(
                f"Config handlers must be supported:\n"
                f"{'\n'.join(f'    - {handler.__name__} (Not Supported)' for handler in invalid_handlers)}"
            )

        return dict(self._associate_extensions_to_handlers(handler_list))

    def _associate_extensions_to_handlers(
        self, handlers: list[Type[ConfigHandler]]
    ) -> Generator[tuple[str, ConfigHandler], None, None]:
        handler_instances = {}
        for handler in handlers:
            for extension in handler.extensions:
                if handler not in handler_instances:
                    handler_instances[handler] = handler()

                yield extension, handler_instances[handler]


def get_active_controller() -> ConfigController:
    return bevy.get_repository().get(ConfigController)


def set_active_controller(controller: ConfigController):
    bevy.get_repository().set(ConfigController, controller)
