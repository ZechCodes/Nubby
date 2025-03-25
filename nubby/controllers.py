from pathlib import Path
from typing import Type, Iterable, Generator

import bevy
from bevy.containers import Container

from nubby.loaders import ConfigLoader

from nubby.models import is_section_model, is_section_model_type, to_dict




class ConfigController:
    def __init__(self, loaders: Iterable[Type[ConfigLoader]] = ()):
        self._paths = []
        self._loaders = self._setup_loaders(loaders)
        self._loaded_configs: dict[str, ConfigLoader] = {}

    def add_path(self, path: Path):
        self._paths.append(self._validate(path))

    def load_config_for[T: "nubby.models.SectionModel"](self, model: "Type[T]") -> T:
        if is_section_model_type(model):
            definition = model.__file_definition__
            filename = definition.file_name
            key = definition.get_key_for(model)
            config = self._get_config_file(filename)
            data = config.load(key)
            return model(**data)

        raise ValueError(f"Model {model.__name__} is not a valid section model")

    def save(self, model: "nubby.models.SectionModel"):
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
    return bevy.get_container(container).get(ConfigController)


def set_active_controller(controller: ConfigController, container: Container | None = None):
    bevy.get_container(container).instances[ConfigController] = controller
