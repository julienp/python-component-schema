from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from analyzer import Analyzer, SchemaProperty


@dataclass
class ItemType:
    type: str

    def to_json(self) -> dict[str, str]:
        return {"type": self.type}


@dataclass
class Property:
    description: Optional[str]
    type: Optional[str]
    will_replace_on_changes: Optional[bool]
    items: Optional[ItemType]
    ref: Optional[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "type": self.type,
            "willReplaceOnChanges": self.will_replace_on_changes,
            "items": self.items,
            "$ref": self.ref,
        }

    @staticmethod
    def from_analyzer(property: SchemaProperty) -> "Property":
        return Property(
            description=property.description,
            type=type_to_str(property.type) if property.type else None,
            will_replace_on_changes=False,
            items=None,
            ref=None,
        )


@dataclass
class Resource:
    is_component: bool
    type: Optional[str]
    input_properties: dict[str, Property]
    required_inputs: list[str]
    properties: dict[str, Property]
    required: list[str]
    description: Optional[str] = None

    def to_json(self) -> dict[str, Any]:
        return {
            "isComponent": self.is_component,
            "description": self.description,
            "type": self.type,
            "inputProperties": {
                k: v.to_json() for k, v in self.input_properties.items()
            },
            "requiredInputs": self.required_inputs,
            "properties": {k: v.to_json() for k, v in self.properties.items()},
            "required": self.required,
        }


@dataclass
class PackageSpec:
    name: str
    displayName: str
    version: str
    resources: dict[str, Resource]

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "displayName": self.displayName,
            "version": self.version,
            "resources": {k: v.to_json() for k, v in self.resources.items()},
        }


def type_to_str(typ: type) -> str:
    if typ is str:
        return "string"
    if typ is int:
        return "integer"
    if typ is float:
        return "number"
    if typ is bool:
        return "boolean"
    return "object"


def generate_schema(name: str, version: str, path: Path) -> PackageSpec:
    s = PackageSpec(
        name=name, displayName="some generated SDK", version=version, resources={}
    )
    components = Analyzer(path).analyze()
    for component_name, component in components.items():
        schema_name = f"{name}:index:{component_name}"
        s.resources[schema_name] = Resource(
            is_component=True,
            type=component_name,
            input_properties={
                k: Property.from_analyzer(property)
                for k, property in component.inputs.items()
            },
            required_inputs=[
                k for k, prop in component.inputs.items() if not prop.optional
            ],
            properties={
                k: Property.from_analyzer(property)
                for k, property in component.outputs.items()
            },
            required=[k for k, prop in component.outputs.items() if not prop.optional],
        )

    return s
