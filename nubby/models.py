from dataclasses import asdict, is_dataclass
from functools import partial
from typing import Any, Callable, cast, NoReturn, overload, Protocol, Type, TypeGuard

import nubby.injectors


class SectionModel(Protocol):
    __file_definition__: "FileModelDefinition" = None

    def __init__(self, **kwargs):
        ...


class FileModelDefinition:
    def __init__(self, file_name: str, *, name_generator: Callable[[str], str] | None = None):
        self.file_name = file_name
        self.sections: dict[Type[SectionModel], str] = {}
        self._name_generator = name_generator or str

    def get_key_for(self, section: Type[SectionModel]) -> str:
        return self.sections[section]

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
                self.sections[section] = name or self._name_generator(section.__name__)
                return section

            case _:
                raise ValueError(f"Invalid arguments to {type(self).__name__}.section: {args}")

    def _convert_to_section_model(self, model: Type[Any]) -> Type[SectionModel]:
        model.__file_definition__ = self
        return cast(Type[SectionModel], model)


@overload
def new_file_model(file_name: str, *, activate: bool) -> FileModelDefinition:
    ...


@overload
def new_file_model(file_name: str, *, activate: bool, generate_normalized_names: bool) -> FileModelDefinition:
    ...


@overload
def new_file_model(file_name: str, *, activate: bool, generate_normalized_names: Callable[[str], str]) -> FileModelDefinition:
    ...


def new_file_model(file_name: str, *, activate: bool = True, **kwargs) -> FileModelDefinition:
    """Creates a new file model definition.

    If generate_normalized_names is True, a snake_case name normalizer is used. If a callable is provided, it is used
    to normalize the name. When omitting this argument or passing False, the model name is used as-is for the config
    section key.
    """
    if activate:
        nubby.injectors.activate()

    pass_kwargs = {}
    match kwargs:
        case {}:
            pass

        case {"generate_normalized_names": bool() as normalized_names}:
            if normalized_names:
                pass_kwargs["name_generator"] = _snake_case_normalizer

        case {"generate_normalized_names": Callable() as generator}:
            pass_kwargs["name_generator"] = generator

        case _:
            raise ValueError(f"Invalid keyword arguments: {kwargs}")

    return FileModelDefinition(file_name, **pass_kwargs)


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
    """Converts a model to a dictionary.

    This attempts to find a supported interface to convert the object to a dictionary. If no interface is found, a
    ValueError is raised.

    Supported interfaces are checked in this order:
        - obj.to_dict()
        - obj.dict()
        - dataclasses.asdict(obj) if is_dataclass(obj) is True

    Providing a to_dict method on a model of any type overrides the other interfaces.
    """
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()

    if hasattr(obj, "dict") and callable(obj.dict):
        return obj.dict()

    if is_dataclass(obj):
        return asdict(obj)

    raise ValueError(f"Object {obj} provides no known interface to convert to a dict.")


def _snake_case_normalizer(name: str) -> str:
    import re

    parts = re.findall(r"[A-Z0-9][a-zA-Z0-9]*", name)
    return "_".join(parts).casefold()