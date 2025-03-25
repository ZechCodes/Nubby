# Nubby

A simple config loader for Python using Bevy for dependency injection. You just need to create a model, declare what
file name it should look for, and mark that model as a dependency wherever you need to have it made available.

## Installation

```bash
pip install nubby
```

You can optionally install the `toml` or `yaml` extras to support those file formats.

```bash
pip install nubby[toml]
pip install nubby[yaml]
```

Out of the box Nubby will use `tomllib` to read TOML files but the `toml` extra installs the `tomlkit` package which
allows writing to TOML files.

## Usage

Nubby is designed to have the smallest possible API surface area. You just need to create a model type that implements
the `SectionModel` interface and declare the file name it should look for. Then you can inject that model wherever you
need it using Bevy.

The file name shouldn't include the file extension. Nubby's file handlers look for supported file extensions in the
search paths. By default, the current working directory is the only search path. You can add more paths using the
`nubby.get_active_controller().add_path` method. It is also possible to add more file handlers using the
`nubby.get_active_controller().add_handler` method.

Here's a basic example of loading a model from a file:

```python
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model


file_definition = new_file_model("person_info")

@file_definition.section("person")
@dataclass
class Person:
    name: str
    age: int


@inject
def print_person_details(person: Person = dependency()):
    print(f"{person.name} is {person.age} years old")
```

Running `print_person_details()` prints the name and age of the person loaded from the `person` section of the `person_info` file.
Depending on the available file handlers it could be a json, toml, or yaml file.

Note that it is not necessary to pass anything to the `print_person_details` function. Nubby uses Bevy to automatically inject the
`Person` model and loads the appropriate config file.

To save any modifications to a model just call the active controller's `save` method, passing it the updated model:

```python
from nubby import get_active_controller

# After modifying the person model
person.age = 32
get_active_controller().save(person)
```

The `save` method will update the in-memory cache as well as the file on disk. It will not update any models that have
already been created.

### Name Normalization

By default, section names in config files match the class name. You can customize this behavior:

```python
# Use snake_case for section names
file_definition = new_file_model("config", generate_normalized_names=True)

@file_definition.section()  # Will use "user_profile" as the section name key in the config file
@dataclass
class UserProfile:
    username: str
    email: str
```

## Supported File Formats

Nubby supports the following file formats out of the box:

- JSON (`.json`)
- TOML (`.toml`) - requires `tomlkit` for writing
- YAML (`.yaml`, `.yml`) - requires `pyyaml`

## License

Nubby is made available under the MIT License.
