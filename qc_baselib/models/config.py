from typing import Annotated, List, Union, Any
from pydantic import Field, model_validator
from pydantic_xml import BaseXmlModel, attr, element

from .common import ParamType

# Configuration models
# Original XSD file:
# > https://github.com/asam-ev/qc-framework/blob/develop/doc/schema/config_format.xsd


class CheckerType(BaseXmlModel, tag="Checker"):
    params: List[ParamType] = []
    checker_id: str = attr(name="checkerId")
    max_level: int = attr(name="maxLevel")
    min_level: int = attr(name="minLevel")


class ReportModuleType(BaseXmlModel, tag="ReportModule"):
    params: List[ParamType] = []
    application: str = attr(name="application")


class CheckerBundleType(BaseXmlModel, tag="CheckerBundle"):
    params: List[ParamType] = []
    checks: List[CheckerType] = []
    application: str = attr(name="application")

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if len(self.params) + len(self.checks) < 1:
            raise ValueError(
                "CheckerBundleType require at least one element of type Param or CheckerType"
            )
        return self


class Config(BaseXmlModel, tag="Config"):
    params: List[ParamType] = []
    reports: List[ReportModuleType] = []
    checker_bundles: List[CheckerBundleType] = []

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if len(self.params) + len(self.reports) + len(self.checker_bundles) < 1:
            raise ValueError("Config require at least one element")
        return self
