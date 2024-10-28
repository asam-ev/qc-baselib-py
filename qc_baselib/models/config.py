# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import List, Any
from pydantic import model_validator
from pydantic_xml import BaseXmlModel, attr, element

from .common import ParamType, IssueSeverity

# Configuration models
# Original XSD file:
# > https://github.com/asam-ev/qc-framework/blob/main/doc/schema/config_format.xsd


class CheckerType(BaseXmlModel):
    params: List[ParamType] = element(tag="Param", default=[])
    checker_id: str = attr(name="checkerId")
    max_level: int = attr(name="maxLevel")
    min_level: int = attr(name="minLevel")


class ReportModuleType(BaseXmlModel):
    params: List[ParamType] = element(tag="Param", default=[])
    application: str = attr(name="application")


class CheckerBundleType(BaseXmlModel, search_mode="unordered"):
    params: List[ParamType] = element(tag="Param", default=[])
    checkers: List[CheckerType] = element(tag="Checker", default=[])
    application: str = attr(name="application")

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if len(self.params) + len(self.checkers) < 1:
            raise ValueError(
                "CheckerBundleType require at least one element of type Param or CheckerType"
            )
        return self


class Config(BaseXmlModel, tag="Config", search_mode="unordered"):
    params: List[ParamType] = element(tag="Param", default=[])
    reports: List[ReportModuleType] = element(tag="ReportModule", default=[])
    checker_bundles: List[CheckerBundleType] = element(tag="CheckerBundle", default=[])

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if len(self.params) + len(self.reports) + len(self.checker_bundles) < 1:
            raise ValueError("Config require at least one element")
        return self
