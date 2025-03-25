"""Nubby comes with built in loaders for JSON, TOML, and YAML files. These loaders are used by default if no loaders are
provided. If a necessary library is not available, the related loader is ignored. You can add each of the loaders
directly if needed."""
from .json import JsonLoader
from .toml import TomlLoader
from .yaml import YamlLoader


__all__ = ["JsonLoader", "TomlLoader", "YamlLoader"]
