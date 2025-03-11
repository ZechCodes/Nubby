from dataclasses import dataclass

from nubby.models import new_file_model, to_dict


def test_model_creation():
    file_model = new_file_model("testing_config", generate_normalized_names=True)

    @file_model.section
    @dataclass
    class Section:
        foo: str
        baz: int

    model = file_model.create_model_builder(
        {
            "section": {"foo": "bar", "baz": 42},
        }
    )
    section_model = model.get(Section)
    assert isinstance(section_model, Section)
    assert section_model.foo == "bar"
    assert section_model.baz == 42


def test_model_upstream_updates():
    file_model = new_file_model("testing_config", generate_normalized_names=True)

    @file_model.section
    @dataclass
    class Section:
        foo: str
        baz: int

    model = file_model.create_model_builder(
        {
            "section": {"foo": "bar", "baz": 42},
        }
    )

    section_model = model.get(Section)
    section_model.foo = "baz"
    section_model.baz = 24

    model.update_section(Section, to_dict(section_model))
    assert model.data["section"]["foo"] == "baz"
    assert model.data["section"]["baz"] == 24