import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, cast

import pulumi
from pulumi.provider import ConstructResult, Provider  # ParameterizeResult

from analyzer import Analyzer
from schema import generate_schema


class ComponentProvider(Provider):
    path: Path

    def __init__(self, name: str, version: str, path: Path) -> None:
        self.path = path
        self.version = version
        self.name = name
        schema = generate_schema(name, version, path)
        super().__init__(version, json.dumps(schema.to_json()))

    # def parameterize_args(self, args: list[str]) -> ParameterizeResult:
    #     return ParameterizeResult(name=self.name, version=self.version)

    def construct(
        self,
        name: str,
        resource_type: str,
        inputs: pulumi.Inputs,
        options: Optional[pulumi.ResourceOptions] = None,
    ) -> ConstructResult:
        component_name = resource_type.split(":")[-1]
        comp, comp_args = self.find_component(component_name)
        args = comp_args(**inputs)
        comp_instance = cast(Any, comp)(name, args, options)
        a = Analyzer(self.path)
        keys = a.analyze_component_outputs(type(comp_instance))
        state = {k: getattr(comp_instance, k, None) for k in keys}
        return ConstructResult(comp_instance.urn, state)

    # TODO: move to analyzer
    def find_component(self, name: str) -> tuple[type[pulumi.ComponentResource], type]:
        for file_path in self.path.iterdir():
            if file_path.suffix != ".py":
                continue
            mod = self._load_module(file_path)
            comp = getattr(mod, name, None)
            if not comp:
                continue
            # TODO: handle kwargs isntead of args param? Args classes vs TypedDict?
            args = comp.__init__.__annotations__.get("args")
            return comp, args
        raise Exception(f"Could not find component {name}")

    def _load_module(self, file_path: Path) -> ModuleType:
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
