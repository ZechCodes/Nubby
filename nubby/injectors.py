"""
This module contains the Bevy hook for injecting Nubby compatible models.

To use this hook, call the activate() function and which adds the hook to the global Bevy registry.

The model_injector hook can be used directly if necessary.
"""
from bevy.containers import Container
from bevy.hooks import hooks
from tramp.optionals import Optional
from typing import Type

import nubby.controllers
from nubby.models import is_section_model_type


def activate():
    """Activates the Nubby model injector hook.

    This is called automatically when creating a new file model definition, but can be called manually if needed.
    """
    model_injector.register_hook()


@hooks.HANDLE_UNSUPPORTED_DEPENDENCY
def model_injector[T](container: Container, dependency: Type[T]) -> Optional[T]:
    """Bevy hook for injecting Nubby compatible models.

    This hook detects if the dependency is a Nubby compatible model and loads the necessary config
    to populate the dependency model.

    To use this hook, add it to a Bevy registry. You can use the model_injector.register_hook()
    method.
    """
    if is_section_model_type(dependency):
        return Optional.Some(
            nubby.controllers.get_active_controller(container).load_config_for(dependency)
        )

    return Optional.Nothing()