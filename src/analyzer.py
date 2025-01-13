from collections.abc import Awaitable
import importlib.util
import sys
import inspect
from types import ModuleType
from typing import (
    ForwardRef,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from dataclasses import dataclass
from pathlib import Path

import pulumi
# from pulumi import Output, Input, Inputs  # noqa
# from pulumi.output import T  # noqa


@dataclass
class SchemaProperty:
    type: Optional[type]
    ref: Optional[str]  # Reference to a type in typeDefinitions
    optional: bool
    description: Optional[str]


@dataclass
class TypeDefinition:
    type: str
    properties: dict[str, SchemaProperty]
    description: Optional[str]


@dataclass
class ComponentSchema:
    description: Optional[str]
    inputs: dict[str, SchemaProperty]
    outputs: dict[str, SchemaProperty]
    type_definitions: dict[str, TypeDefinition]


class Analyzer:
    def __init__(self, path: Path):
        self.path = path

    def analyze(self) -> dict[str, ComponentSchema]:
        components: dict[str, ComponentSchema] = {}
        for file_path in self.path.iterdir():
            if file_path.suffix != ".py":
                continue
            comps = self.analyze_file(file_path)
            components.update(comps)
        return components

    def analyze_file(self, file_path: Path) -> dict[str, ComponentSchema]:
        components: dict[str, ComponentSchema] = {}
        module_type = self._load_module(str(file_path))
        for name in dir(module_type):
            obj = getattr(module_type, name)
            if inspect.isclass(obj):
                if pulumi.ComponentResource in obj.__bases__:
                    component = self.analyze_component(obj)
                    components[name] = component
        return components

    def _load_module(self, file_path: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location("component", file_path)
        if not spec:
            raise Exception(f"Could not load module spec at {file_path}")
        module_type = importlib.util.module_from_spec(spec)
        name = "my_module"  # TODO: get name from file_path?
        sys.modules[name] = module_type
        if not spec.loader:
            raise Exception(f"Could not load module at {file_path}")
        spec.loader.exec_module(module_type)
        return module_type

    def analyze_component(
        self,
        component: type[pulumi.ComponentResource],
    ) -> ComponentSchema:
        args = component.__init__.__annotations__.get("args")
        if not args:
            raise Exception(f"Could not find in {component}'s __init__ method")
        return ComponentSchema(
            description="",
            inputs=self.analyze_types(args),
            outputs=self.analyze_types(component),
            type_definitions={},
        )

    def analyze_types(self, typ: type) -> dict[str, SchemaProperty]:
        print(f"__annotations__ {typ.__annotations__}")
        # TODO: should we use get_type_hints instead to resolve ForwardRefs?
        # What's the global context?
        # hints = get_type_hints(typ, globalns=globals())
        # print(f"hints: {hints}")
        return {k: self.analyze_arg(typ) for k, typ in typ.__annotations__.items()}

    def analyze_arg(self, arg: type) -> SchemaProperty:
        print(f"\ntype(arg): {type(arg)}")
        origin = get_origin(arg)
        print(f"origin: {origin}")
        args_t = get_args(arg)
        print(f"args_t: {args_t}")
        arg_is_optional = is_optional(arg)
        print(f"arg_is_optional: {arg_is_optional}")
        arg_is_input = is_input(arg)
        print(f"arg_is_input: {arg_is_input}")
        arg_is_output = is_output(arg)
        print(f"arg_is_output: {arg_is_output}")
        arg_is_plain = is_plain(arg)
        if arg_is_plain:
            unwrapped = arg
        elif arg_is_input:
            unwrapped = unwrap_input(arg)
        elif arg_is_output:
            unwrapped = unwrap_output(arg)
        elif arg_is_optional:
            unwrapped = unwrap_optional(arg)
        else:
            raise ValueError(f"Unsupported type {arg}")
        # TODO:
        #  * typed dict arguments type, instead of args class
        #  * list property
        #  * typed dict property?

        return SchemaProperty(
            type=unwrapped,
            ref=None,
            optional=arg_is_optional,
            description="",
        )


def is_plain(typ: type) -> bool:
    """
    A plain type is not an Output or an Optional.
    """
    return typ in (str, int, float, bool)


def is_optional(typ: type) -> bool:
    """
    A Union that includes None is an optional type.
    """
    origin = get_origin(typ)
    args = get_args(typ)
    if origin is not None and origin == Union:
        return type(None) in args
    return False


def unwrap_optional(typ: type) -> Optional[type]:
    """
    Returns the first non-None type of the optional type.
    """
    if not is_optional(typ):
        raise ValueError("Not an optional type")
    elements = get_args(typ)
    for element in elements:
        if element is not type(None):
            return element
    raise ValueError("Optional type with no non-None elements")


def is_output(typ: type):
    """
    A type is an output if it is a pulumi.Output or a Union that includes pulumi.Output.
    """
    origin = get_origin(typ)
    if is_optional(typ):
        return any(is_output(arg) for arg in get_args(typ))
    # elif is_forward_ref(typ):
    #     return typ.__forward_arg__ == "Output[T]"
    else:
        return origin is not None and origin == pulumi.Output


def unwrap_output(typ: type) -> Optional[type]:
    if is_optional(typ):
        elements = get_args(typ)
        for element in elements:
            if is_output(element):
                args = get_args(element)
                return args[0]
    if not is_output(typ):
        return None
    args = get_args(typ)
    return args[0]


# Input = Union[T, Awaitable[T], "Output[T]"]
# Inputs = Mapping[str, Input[Any]]
# InputType = Union[T, Mapping[str, Any]]


def is_input(typ: type) -> bool:
    print(f"is_input {str(typ)}")
    origin = get_origin(typ)
    if origin is not None and origin == Union:
        has_awaitable = False
        has_output = False
        base_type = None

        typeVar = get_typevar(typ)
        print(f"typeVar: {typeVar}")

        for element in get_args(typ):
            if get_origin(element) is Awaitable:
                args = get_args(element)
                print(f"awaitable args = {args}")
                has_awaitable = True
                base_type = args[0]
            if is_output(element):
                has_output = True
            if is_forward_ref(element):
                if element.__forward_arg__ == "Output[T]":
                    has_output = True

        print(f"has_awaitable: {has_awaitable}")
        print(f"has_output: {has_output}")
        print(f"base_type: {base_type}")
        if has_awaitable and has_output and base_type is not None:
            return True
    return False


def unwrap_input(typ: type) -> type:
    if not is_input(typ):
        raise ValueError("Not an input type")
    args = get_args(typ)
    for element in args:
        if get_origin(element) is Awaitable:
            return get_args(element)[0]
    raise ValueError("Input type with no Awaitable elements")


def is_typevar(typ: type) -> bool:
    return typ is TypeVar


def get_typevar(typ: type) -> Optional[type]:
    if typ is TypeVar:
        return typ
    elif get_origin(typ) is Union:
        for arg in get_args(typ):
            if arg is TypeVar:
                return arg
    return None


def is_forward_ref(typ: type) -> bool:
    return isinstance(typ, ForwardRef)
