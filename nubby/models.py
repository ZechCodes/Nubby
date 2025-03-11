from dataclasses import asdict, is_dataclass
from functools import partial
from typing import Any, Callable, cast, NoReturn, overload, Protocol, Type, TypeGuard

from bevy.hooks import hooks
from bevy.containers import Container
from tramp.optionals import Optional
import nubby.controllers


class SectionModel(Protocol):
    __file_definition__: "FileModelDefinition" = None

    def __init__(self, **kwargs):
        ...


class ConfigFile:
    def __init__(self, file_model: "FileModelDefinition", data: dict[str, Any]):
        self.file_model = file_model
        self.data = data

    @overload
    def get(self, section_model: Any) -> NoReturn:
        ...

    @overload
    def get(self, section_model: Type[SectionModel]) -> SectionModel:
        ...

    def get[T: SectionModel | Any](self, section_model: Type[T]) -> T:
        if not is_section_model_type(section_model):
            raise ValueError(f"{section_model} is not a valid section model type")

        return section_model(
            **self.data[self.file_model.sections[section_model]]
        )

    @overload
    def update_section(self, section: Any, data: dict[str, Any]) -> NoReturn:
        ...

    @overload
    def update_section(self, section: Type[SectionModel], data: dict[str, Any]) -> None:
        ...

    def update_section(self, section: Type[SectionModel], data: dict[str, Any]):
        if not is_section_model_type(section):
            raise ValueError(f"{section} is not a valid section model type")

        self.data[self.file_model.sections[section]] = data


class FileModelDefinition:
    def __init__(self, file_name: str, *, name_generator: Callable[[str, str], str] | None = None):
        self.file_name = file_name
        self.sections: dict[Type[SectionModel], str] = {}
        self._name_generator = name_generator or self._default_name_generator

    def create_model_builder(self, data: dict[str, Any]) -> ConfigFile:
        return ConfigFile(self, data)

    @overload
    def section(self, name: str) -> Callable[[Type[Any]], Type[SectionModel]]:
        ...

    @overload
    def section(self, model: Type[Any]) -> Type[SectionModel]:
        ...

    @overload
    def section(self, name: str, model: Type[Any]) -> Type[SectionModel]:
        ...

    def section(self, *args) -> Callable[[Type[Any]], Type[SectionModel]] | Type[SectionModel]:
        match args:
            case [str() as name]:
                return partial(self.section, name)

            case [type() as model]:
                return self.section("", model)

            case [str() as name, type() as model]:
                section = self._convert_to_section_model(model)
                self.sections[section] = self._name_generator(name, section.__name__)
                return section

            case _:
                raise ValueError(f"Invalid arguments to {type(self).__name__}.section: {args}")

    def _convert_to_section_model(self, model: Type[Any]) -> Type[SectionModel]:
        model.__file_definition__ = self
        return cast(Type[SectionModel], model)

    def _default_name_generator(self, name: str, model_name: str) -> str:
        return name or model_name


@hooks.HANDLE_UNSUPPORTED_DEPENDENCY
def model_injector[T](container: Container, dependency: Type[T]) -> Optional[T]:
    if is_section_model_type(dependency):
        return Optional.Some(
            nubby.controllers.get_active_controller(container).load_config_for(dependency)
        )

    return Optional.Nothing()


def new_file_model(file_name: str, *, generate_normalized_names: bool = False) -> FileModelDefinition:
    kwargs = {}
    if generate_normalized_names:
        kwargs["name_generator"] = lambda name, model_name: name or _normalized_name(model_name)

    return FileModelDefinition(file_name, **kwargs)


def is_section_model(c: Any) -> TypeGuard[SectionModel]:
    if not hasattr(c, "__file_definition__"):
        return False

    return True


def is_section_model_type(c: Type[Any]) -> TypeGuard[Type[SectionModel]]:
    if not is_section_model(c):
        return False

    if not isinstance(c, type):
        return False

    return True


def to_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()

    if hasattr(obj, "dict") and callable(obj.dict):
        return obj.dict()

    if is_dataclass(obj):
        return asdict(obj)

    raise ValueError(f"Object {obj} provides no known interface to convert to a dict.")


def _normalized_name(name: str) -> str:
    import re

    parts = re.findall(r"[A-Z0-9][a-zA-Z0-9]*", name)
    return "_".join(parts).casefold()