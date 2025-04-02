# Getting Started with Nubby

This guide will help you get started with Nubby, a simple configuration loader for Python that uses Bevy for dependency injection.

## Installation

First, install Nubby using pip:

```bash
pip install nubby
```

Nubby supports JSON out of the box. For additional format support, install the appropriate extras:

```bash
# For YAML support
pip install nubby[yaml]

# For TOML writing support
pip install nubby[toml]
```

## Basic Usage

### 1. Define a Configuration File

Start by defining a configuration file using the `new_file_model` function:

```python
from nubby.models import new_file_model

# Create a file definition for a file named "app_config"
# This will look for app_config.json, app_config.yaml, or app_config.toml
file_definition = new_file_model("app_config")
```

### 2. Define Configuration Sections

Next, define the sections of your configuration file using the `section` decorator:

```python
from dataclasses import dataclass

@file_definition.section("database")
@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str

@file_definition.section("logging")
@dataclass
class LoggingConfig:
    level: str
    file: str
```

### 3. Use the Configuration

Now you can use the configuration in your code using Bevy's dependency injection:

```python
from bevy import inject, dependency

@inject
def connect_to_database(db_config: DatabaseConfig = dependency()):
    # db_config is automatically loaded from the configuration file
    print(f"Connecting to {db_config.host}:{db_config.port}")
    # ... connection logic ...

@inject
def setup_logging(log_config: LoggingConfig = dependency()):
    # log_config is automatically loaded from the configuration file
    print(f"Setting up logging with level {log_config.level}")
    # ... logging setup logic ...
```

### 4. Create a Configuration File

Create a configuration file in one of the supported formats. For example, `app_config.json`:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "username": "user",
    "password": "password"
  },
  "logging": {
    "level": "INFO",
    "file": "app.log"
  }
}
```

### 5. Run Your Application

When you run your application, Nubby will automatically find and load the configuration file, and Bevy will inject the configuration into your functions.

## Advanced Usage

### Custom Search Paths

By default, Nubby looks for configuration files in the current working directory. You can add additional search paths:

```python
from nubby import get_active_controller

# Add a search path
get_active_controller().add_path("/etc/myapp")
get_active_controller().add_path("~/.config/myapp")
```

### Saving Configuration Changes

You can save changes to a configuration back to the file:

```python
from nubby import get_active_controller

# After modifying the configuration
db_config.port = 5433
get_active_controller().save(db_config)
```

### Custom Name Normalization

You can customize how section names are generated:

```python
# Use snake_case for section names
file_definition = new_file_model("config", name_generator=lambda s: s.lower())

@file_definition.section()  # Will use "userprofile" as the section name
@dataclass
class UserProfile:
    username: str
    email: str
```

## Next Steps

- Check out the [Usage Guide](usage-guide.md) for more detailed information
- Explore the [API Reference](api-reference.md) for complete documentation
- See the [Examples](examples.md) for practical use cases
