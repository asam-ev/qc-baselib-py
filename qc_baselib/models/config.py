# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List, Any
from pydantic import model_validator
from pydantic_xml import BaseXmlModel, attr

from .common import ParamType, IssueSeverity

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
    checkers: List[CheckerType] = []
    application: str = attr(name="application")

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if len(self.params) + len(self.checkers) < 1:
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
