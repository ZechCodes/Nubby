from pathlib import Path
from typing import Type, Iterable, Generator, TYPE_CHECKING

import bevy
from bevy.containers import Container

from nubby.handlers import ConfigHandler

if TYPE_CHECKING:
    import nubby.models


class ConfigFile:
    def __init__(self, data: dict[str, dict], handler: ConfigHandler, path: Path):
        self.data = data
        self.handler = handler
        self.path = path


class ConfigController:
    def __init__(self, handlers: Iterable[Type[ConfigHandler]] = ()):
        self._paths = []
        self._handlers = self._setup_handlers(handlers)
        self._config_cache: dict[str, ConfigFile] = {}

    def add_path(self, path: Path):
        self._paths.append(
            self._validate(path)
        )

    def add_handler(self, handler: Type[ConfigHandler]):
        self._handlers.update(self._associate_extensions_to_handlers([handler]))

    def load_config_for[T: "nubby.models.SectionModel"](self, model: "Type[T]") -> T:
        file_model = model.__file_definition__
        filename = file_model.file_name
        config = self._get_config_file_with_cache(filename)
        data = config.data
        if model.__config_key__:
            data = data.get(model.__config_key__)
            if data is None:
                raise KeyError(
                    f"Config key {model.__config_key__!r} for {model.__module__}.{model.__qualname__} not found in "
                    f"{filename!r}"
                )

        return model(**data)

    def save(self, model: "nubby.models.SectionModel"):
        file_definition = model.__file_definition__
        filename = file_definition.file_name
        config = self._get_config_file_with_cache(filename)

        config_file.update
        if model.__config_key__:
            config.data[model.__config_key__] = model.to_dict()

        else:
            config.data = model.to_dict()

        with config.path.open("wb") as file:
            config.handler.write(config.data, file)

    def _find_config_file(self, filename: str) -> tuple[Path, ConfigHandler]:
        for path in self._get_paths():
            for extension, handler in self._handlers.items():
                file_path = path / f"{filename}.{extension}"
                if file_path.exists():
                    return file_path, handler

        raise FileNotFoundError(
            f"Config file {filename!r} not found in paths:\n"
            f"{'\n'.join(f'    - {path}' for path in self._get_paths())}"
        )

    def _get_config_file_with_cache(self, filename: str) -> ConfigFile:
        file_path, handler = self._find_config_file(filename)
        if file_path not in self._config_cache:
            with file_path.open("rb") as file:
                self._config_cache[filename] = ConfigFile(handler.load(file), handler, file_path)

        return self._config_cache[filename]

    def _get_paths(self) -> list[Path]:
        if self._paths:
            return self._paths

        return [Path.cwd()]

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

    def _validate(self, path: Path | str) -> Path:
        match path:
            case Path() if path.is_dir():
                return path

            case str():
                return self._validate(Path(path))

            case Path() if not path.is_dir():
                raise ValueError("Path must be a directory, not a file")

            case _:
                raise ValueError(f"Received an invalid path value: {path!r}")


    @staticmethod
    def _associate_extensions_to_handlers(
        handlers: list[Type[ConfigHandler]]
    ) -> Generator[tuple[str, ConfigHandler], None, None]:
        handler_instances = {}
        for handler in handlers:
            for extension in handler.extensions:
                if handler not in handler_instances:
                    handler_instances[handler] = handler()

                yield extension, handler_instances[handler]


def get_active_controller(container: Container | None = None) -> ConfigController:
    return bevy.get_container(container).get(ConfigController)


def set_active_controller(controller: ConfigController, container: Container | None = None):
    bevy.get_container(container).instances[ConfigController] = controller
