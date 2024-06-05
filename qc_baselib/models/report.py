# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
import enum

from typing import List, Any
from pydantic import model_validator
from pydantic_xml import BaseXmlModel, attr

from .common import ParamType


class IssueSeverity(enum.IntEnum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3


# Report models
# Original XSD file:
# > https://github.com/asam-ev/qc-framework/blob/develop/doc/schema/xqar_report_format.xsd


class XMLLocationType(BaseXmlModel, tag="XMLLocation"):
    xpath: str = attr(name="xpath")


class RoadLocationType(BaseXmlModel, tag="RoadLocation"):
    road_id: int = attr(name="roadId")
    t: str = attr(name="t")
    s: str = attr(name="s")


class FileLocationType(BaseXmlModel, tag="FileLocation"):
    column: int = attr(name="column")
    row: int = attr(name="row")
    file_type: str = attr(name="fileType")


class LocationType(BaseXmlModel, tag="Location"):
    file_location: List[FileLocationType] = []
    xml_location: List[XMLLocationType] = []
    road_location: List[RoadLocationType] = []
    description: str = attr(name="description")

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if (
            len(self.file_location) + len(self.xml_location) + len(self.road_location)
            < 1
        ):
            raise ValueError(
                "LocationType require at least one element of type XMLLocationType / FileLocationType / RoadLocationType"
            )
        return self


class IssueType(BaseXmlModel, tag="Issue"):
    locations: List[LocationType] = []
    issue_id: int = attr(name="issueId")
    description: str = attr(name="description")
    level: IssueSeverity = attr(name="level")


class CheckerType(BaseXmlModel, tag="Checker"):
    issues: List[IssueType] = []
    checker_id: str = attr(name="checkerId")
    description: str = attr(name="description")
    summary: str = attr(name="summary")


class CheckerBundleType(BaseXmlModel, tag="CheckerBundle"):
    params: List[ParamType] = []
    checkers: List[CheckerType] = []
    build_date: str = attr(name="build_date")
    description: str = attr(name="description")
    name: str = attr(name="name")
    version: str = attr(name="version")
    summary: str = attr(name="summary")


class CheckerResults(BaseXmlModel, tag="CheckerResults"):
    checker_bundles: List[CheckerBundleType] = []
    version: str = attr(name="version")
