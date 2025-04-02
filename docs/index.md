# Nubby

**A simple config loader for Python using Bevy for dependency injection**

[![PyPI version](https://img.shields.io/pypi/v/nubby.svg)](https://pypi.org/project/nubby/)
[![Python versions](https://img.shields.io/pypi/pyversions/nubby.svg)](https://pypi.org/project/nubby/)
[![License](https://img.shields.io/github/license/zechdc/nubby.svg)](https://github.com/zechdc/nubby/blob/main/LICENSE)

## Overview

Nubby is a lightweight, intuitive configuration management library for Python applications. It seamlessly integrates with the Bevy dependency injection system to provide a clean, type-safe way to manage configuration.

## Key Features

- **Simple API**: Minimal API surface area makes it easy to learn and use
- **Type Safety**: Leverages Python's type annotations for type-safe configuration
- **Dependency Injection**: Built on Bevy for seamless dependency injection
- **Multiple Formats**: Supports JSON, TOML, and YAML configuration formats
- **Extensible**: Easy to add custom loaders for other formats
- **Automatic Loading**: Automatically finds and loads configuration files
- **Path Management**: Flexible configuration file search paths

## Installation

```bash
pip install nubby
```

For additional format support:

```bash
# For YAML support
pip install nubby[yaml]

# For TOML writing support
pip install nubby[toml]
```

## Quick Example

```python
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model

# Define a configuration file
file_definition = new_file_model("app_config")

# Define a configuration section
@file_definition.section("database")
@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str

# Use the configuration anywhere in your code
@inject
def connect_to_database(db_config: DatabaseConfig = dependency()):
    # db_config is automatically loaded from the configuration file
    print(f"Connecting to {db_config.host}:{db_config.port}")
    # ... connection logic ...
```

## Why Nubby?

Nubby was designed to make configuration management in Python applications as simple and type-safe as possible. By leveraging Python's type annotations and the Bevy dependency injection system, Nubby provides a clean, intuitive API for managing configuration.

Unlike other configuration libraries, Nubby:

- Doesn't require manual loading of configuration files
- Provides type safety through Python's type annotations
- Integrates seamlessly with dependency injection
- Has a minimal API surface area
- Is extensible with custom loaders

Check out the [Getting Started](getting-started.md) guide to learn more!
