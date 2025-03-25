"""
Nubby is a simple config loader for Python using Bevy for dependency injection. You just need to create a file
definition, create section models, and mark those models as a dependencies wherever you need to have them made
available.

Example:
    file_definition = new_file_model("example")

    @file_definition.section("data")
    @dataclass
    class DataModel:
        message: str

    @inject
    def print_message(data: DataModel = dependency()):
        print(data.message)

Nubby handles locating the config file, loading the data into the DataModel, and Bevy injects the DataModel instance
into the print_message function.

Out of the box Nubby comes with loaders for JSON, TOML, and YAML files. These loaders are used by default if no loaders
are provided. If a necessary library is not available, the related loader is ignored.

To use a custom loader, pass it to the ConfigController constructor at the start of your application:

    setup_controller([MyCustomLoader])
"""
from nubby.injectors import activate, model_injector
from nubby.models import new_file_model
from nubby.controllers import get_active_controller, setup_controller


__all__ = ["activate", "model_injector", "new_file_model", "get_active_controller", "setup_controller"]
