# API Reference

This section contains the API reference for Nubby. It is automatically generated from the docstrings in the code.

## Core Module

The core module provides the main functionality of Nubby.

```python
from nubby import activate, model_injector, new_file_model, get_active_controller, setup_controller
```

## Models

The models module provides the necessary interfaces to define the shape of config files.

```python
from nubby.models import new_file_model, FileModelDefinition, SectionModel
```

## Controllers

The controllers module provides the ConfigController class which manages config files.

```python
from nubby.controllers import get_active_controller, setup_controller, ConfigController
```

## Injectors

The injectors module contains the Bevy hook for injecting Nubby compatible models.

```python
from nubby.injectors import activate, model_injector
```

## Loaders

The loaders module provides the base ConfigLoader class and related functionality.

```python
from nubby.loaders import ConfigLoader
```

## Built-in Loaders

Nubby comes with built-in loaders for JSON, TOML, and YAML files.

```python
from nubby.builtins.loaders import JsonLoader, TomlLoader, YamlLoader
```
