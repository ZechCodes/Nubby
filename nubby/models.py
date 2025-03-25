"""
This module provides the necessary interfaces necessary to define the shape of config files so that they can be
dynamically loaded by Nubby.

Nubby uses Bevy for dependency injection, to do that, it needs to know what models are available and how to load them.
To accomplish this a FileDefinitionModel is used to store metadata about the config file: the file name, how section
names should be generated, and the models that are exist for the file.

The file type is determined by the file extension. Nubby will look for supported file extensions in the search paths. So
the file name should just be the name of the file without an extension.

To define a config file, use the new_file_model function. This returns a FileDefinitionModel that can be used to define
the sections of the config file. Section models can then be defined using the definition's section decorator.

Example:
    file_definition = new_file_model("example")

    @file_definition.section("data")
    @dataclass
    class DataModel:
        key: str

This example definition supports any config file with the name example.json, example.toml, example.yaml,
etc. and a top level key named "data". That top level key is used to load the data into the DataModel.
"""
from dataclasses import asdict, is_dataclass
from functools import partial
from typing import Any, Callable, cast, NoReturn, overload, Protocol, Type, TypeGuard

import nubby.injectors


class SectionModel(Protocol):
    """Protocol for models that can be loaded from a config file."""
    __file_definition__: "FileModelDefinition" = None

    def __init__(self, **kwargs):
        ...


class FileModelDefinition:
    """Defines a Nubby config file. It holds the file name and the sections that are defined in the file.
    Each section is associated with a model type. It also provides a way to get the key for a given section by
    normalizing section model names.

    To add declare a model as a file section use the section decorator. The decorator can take an optional section name.
    If no name is provided, the model name is used, and may be normalized if a name generator is available.

    Example:
        file_definition = new_file_model("example")

        @file_definition.section("data")
        @dataclass
        class DataModel:
            key: str

    This example definition supports any config file with the name example.json, example.toml, example.yaml,
    etc. and a top level key named "data". That top level key is used to load the data into the DataModel.
    """
    def __init__(self, file_name: str, *, name_generator: Callable[[str], str] | None = None):
        self.file_name = file_name
        self.sections: dict[Type[SectionModel], str] = {}
        self._name_generator = name_generator or str

    def get_key_for(self, section: Type[Any]) -> str:
        """Returns the key for a given section model. If the section is not defined in this file definition, a ValueError
        is raised.
        """
        if is_section_model_type(section):
            if section in self.sections:
                return self.sections[section]
            raise KeyError(f"Section {section.__name__} is not defined in this file definition")
        raise ValueError(f"Section {section.__name__} is not a valid section model")

    @overload
    def section(self) -> Callable[[Type[Any]], Type[SectionModel]]:
        ...

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
        """A decorator that adds a section model to the file definition and modifies it to adhere to the SectionModel
        protocol. The name is used as the key in the config file. If no name is provided, the model name is used and may
        be normalized if a name generator is available for the file definition.
        """
        match args:
            case []:
                return self.section

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
        """Converts a model to a section model by adding the file definition to the model."""
        model.__file_definition__ = self
        return cast(Type[SectionModel], model)


@overload
def new_file_model(file_name: str, *, activate: bool = True) -> FileModelDefinition:
    ...


@overload
def new_file_model(file_name: str, *, activate: bool = True, generate_normalized_names: bool) -> FileModelDefinition:
    ...


@overload
def new_file_model(
    file_name: str, *, activate: bool = True, generate_normalized_names: Callable[[str],str]
) -> FileModelDefinition:
    ...


def new_file_model(file_name: str, *, activate: bool = True, **kwargs) -> FileModelDefinition:
    """Creates a new file model definition.

    This activates the model injector by default. If you don't want this behavior, pass activate=False.

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