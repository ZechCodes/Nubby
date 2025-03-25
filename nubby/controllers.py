"""This module provides the ConfigController class which manages config files by searching for files and loading them
using the appropriate loader.

The controller provides methods to create model instances populated from config files and to write data in model
instances into config files.

The controller is intended to be stored in a Bevy container and used as a dependency of functions in the same context.
This allows configs to be cached.
"""
from pathlib import Path
from typing import overload, Type, Iterable, Generator

import bevy
from bevy.containers import Container
from tramp import matches

from nubby.loaders import ConfigLoader

from nubby.models import is_section_model, is_section_model_type, to_dict


class ConfigController:
    """The ConfigController is responsible for loading and saving config files.

    It is responsible for finding the correct config file for a given model and loading the data into the model. It also
    provides a way to save changes to a model back to the config file.

    The controller holds all loader types and config file search paths. It also holds a cache of loaded config file
    loaders.

    When a model needs to be populated, the controller searches for a file in the search paths that has an extension
    that is supported by a loader. If no file is found, a FileNotFoundError is raised. If a file is found,
    the path is passed to the loader and then the section key is loaded from the loader.

    Once the data is loaded, the loader instance is stored for later reuse. It is up to the loader to cache the config
    data.
    """
    def __init__(self, loaders: Iterable[Type[ConfigLoader]] = ()):
        self._paths = []
        self._loaders = self._setup_loaders(loaders)
        self._loaded_configs: dict[str, ConfigLoader] = {}

    def add_path(self, path: Path):
        """Adds a path to the config file search paths. Any previously loaded config files are not affected."""
        self._paths.append(self._validate(path))

    def load_config_for[T: "nubby.models.SectionModel"](self, model: "Type[T]") -> T:
        """Loads a config file for a given model and returns an instance of the model."""
        if is_section_model_type(model):
            definition = model.__file_definition__
            filename = definition.file_name
            key = definition.get_key_for(model)
            config = self._get_config_file(filename)
            data = config.load(key)
            return model(**data)

        raise ValueError(f"Model {model.__name__} is not a valid section model")

    def save(self, model: "nubby.models.SectionModel"):
        """Writes the data in a model instance into the associated config file."""
        if is_section_model(model):
            definition = model.__file_definition__
            filename = definition.file_name
            key = definition.get_key_for(type(model))
            config = self._get_config_file(filename)
            data = config.load()
            data[key] = to_dict(model)
            config.write(data)

        else:
            raise ValueError(f"Model {type(model).__name__} is not a section model")

    def _find_config_file(self, filename: str) -> tuple[Path, Type[ConfigLoader]]:
        for path in self._get_paths():
            for extension, loader in self._loaders.items():
                file_path = path / f"{filename}.{extension}"
                if file_path.exists():
                    return file_path, loader

        raise FileNotFoundError(
            f"Config file {filename!r} not found in paths:\n"
            f"{'\n'.join(f'    - {path}' for path in self._get_paths())}"
        )

    def _get_config_file(self, filename: str) -> ConfigLoader:
        file_path, loader = self._find_config_file(filename)
        if file_path not in self._loaded_configs:
            self._loaded_configs[filename] = loader(file_path)

        return self._loaded_configs[filename]

    def _get_paths(self) -> list[Path]:
        if self._paths:
            return self._paths

        return [Path.cwd()]

    def _setup_loaders(self, loaders: Iterable[Type[ConfigLoader]]) -> dict[str, Type[ConfigLoader]]:
        loader_list = list(loaders)

        if not loader_list:
            import nubby.builtins.loaders as loaders
            loader_list = [
                loader
                for loader in vars(loaders).values()
                if isinstance(loader, type) and issubclass(loader, ConfigLoader) and loader.supported()
            ]

        elif invalid_loaders := [loader for loader in loader_list if not loader.supported()]:
            raise ValueError(
                f"Config loaders must be supported:\n"
                f"{'\n'.join(f'    - {loader.__name__} (Not Supported)' for loader in invalid_loaders)}"
            )

        return dict(self._associate_extensions_to_loaders(loader_list))

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
    def _associate_extensions_to_loaders(
        loaders: list[Type[ConfigLoader]]
    ) -> Generator[tuple[str, Type[ConfigLoader]], None, None]:
        loader_instances = {}
        for loader in loaders:
            for extension in loader.extensions:
                if loader not in loader_instances:
                    loader_instances[loader] = loader

                yield extension, loader_instances[loader]


def get_active_controller(container: Container | None = None) -> ConfigController:
    """Returns the active config controller instance in the Bevy container. If no container is provided, the global
    container is used.

    If no active controller is found, a new controller is created and set as the active controller.
    """
    return bevy.get_container(container).get(ConfigController)


def set_active_controller(controller: ConfigController, container: Container | None = None):
    """Sets the active config controller instance in the Bevy container. If no container is provided, the global
    container is used.
    """
    bevy.get_container(container).instances[ConfigController] = controller


@overload
def setup_controller(*, container: Container | None = None):
    ...


@overload
def setup_controller(loader: Type[ConfigLoader], *, container: Container | None = None):
    ...


@overload
def setup_controller(loaders: Iterable[Type[ConfigLoader]], *, container: Container | None = None):
    ...


def setup_controller(*args, container: Container | None = None):
    """Sets up the active config controller instance in the Bevy container. If no container is provided, the global
    container is used. If a controller is already set, it is replaced with a new controller.

    The loaders argument is passed to the ConfigController constructor. If loaders is empty it uses the default loaders.
    """
    match args:
        case []:
            loaders = []

        case [ConfigLoader() as loader]:
            loaders = [loader]

        case [matches.Iterable() as loaders]:
            pass

        case _:
            raise ValueError(f"Invalid arguments: {args}")

    set_active_controller(ConfigController(loaders), container)
