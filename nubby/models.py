import nubby.controllers


class ConfigModel:
    __config_filename__: str
    __config_key__: str

    def __init_subclass__(cls, **kwargs):
        lax = kwargs.pop("lax", False)
        cls.__config_filename__ = kwargs.pop("filename", getattr(cls, "__config_filename__", ""))
        cls.__config_key__ = kwargs.pop("key", getattr(cls, "__config_key__", ""))

        if not lax and not cls.__config_filename__:
            bases = ", ".join(base.__name__ for base in cls.__bases__)
            raise ValueError(
                f"You must specify a config filename for {cls.__module__}.{cls.__qualname__}.\n"
                f"    ex. class {cls.__name__}({bases}, filename='example_file_name'):\n"
                f"    The file extension must be excluded."
            )

        super().__init_subclass__(**kwargs)

    @classmethod
    def __bevy_constructor__(cls):
        return nubby.controllers.get_active_controller().load_config_for(cls)