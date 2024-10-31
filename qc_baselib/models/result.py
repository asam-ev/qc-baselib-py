# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
import enum


from typing import List, Any, Set
from pydantic import model_validator
from pydantic_xml import BaseXmlModel, attr, element, computed_element
from lxml import etree

from .common import ParamType, IssueSeverity


# Report models
# Original XSD file:
# > https://github.com/asam-ev/qc-framework/blob/main/doc/schema/xqar_report_format.xsd


class XMLLocationType(BaseXmlModel):
    xpath: str = attr(name="xpath")


class InertialLocationType(BaseXmlModel):
    x: float = attr(name="x")
    y: float = attr(name="y")
    z: float = attr(name="z")


class FileLocationType(BaseXmlModel):
    column: int = attr(name="column")
    row: int = attr(name="row")


class LocationType(BaseXmlModel, search_mode="unordered"):
    file_location: List[FileLocationType] = element(tag="FileLocation", default=[])
    xml_location: List[XMLLocationType] = element(tag="XMLLocation", default=[])
    inertial_location: List[InertialLocationType] = element(
        tag="InertialLocation", default=[]
    )
    description: str = attr(name="description")

    @model_validator(mode="after")
    def check_at_least_one_element(self) -> Any:
        if (
            len(self.file_location)
            + len(self.xml_location)
            + len(self.inertial_location)
            < 1
        ):
            raise ValueError(
                "LocationType require at least one element of type XMLLocationType / FileLocationType / RoadLocationType"
            )
        return self


class RuleType(BaseXmlModel):
    """
    Type containing the Rule Schema rules and its required checks

    More information at:
        https://github.com/asam-ev/qc-framework/blob/main/doc/manual/rule_uid_schema.md
    """

    # The current implementation makes Rule members required, so no element can
    # be left empty for the uid composition.

    emanating_entity: str = attr(
        name="emanating_entity", default="", pattern=r"^((\w+(\.\w+)+))$", exclude=True
    )
    standard: str = attr(
        name="standard", default="", pattern=r"^(([a-z]+))$", exclude=True
    )
    definition_setting: str = attr(
        name="definition_setting",
        default="",
        pattern=r"^(([0-9]+(\.[0-9]+)+))$",
        exclude=True,
    )
    rule_full_name: str = attr(
        name="rule_full_name",
        default="",
        pattern=r"^((([a-z][\w_]*)\.)*)([a-z][\w_]*)$",
        exclude=True,
    )

    rule_uid: str = attr(
        name="ruleUID",
        default="",
        pattern=r"^((\w+(\.\w+)+)):(([a-z]+)):(([0-9]+(\.[0-9]+)+)):((([a-z][\w_]*)\.)*)([a-z][\w_]*)$",
    )

    @model_validator(mode="after")
    def load_fields_into_uid(self) -> Any:
        """
        Loads fields into rule uid if all required fields are present.
        Otherwise it skips initialization.
        """
        if (
            self.emanating_entity != ""
            and self.standard != ""
            and self.definition_setting != ""
            and self.rule_full_name != ""
        ):
            self.rule_uid = f"{self.emanating_entity}:{self.standard}:{self.definition_setting}:{self.rule_full_name}"

        return self

    @model_validator(mode="after")
    def load_uid_into_fields(self) -> Any:
        """
        Loads fields from rule uid if no field is present in the model.
        Otherwise it skips initialization.
        """
        if (
            self.emanating_entity == ""
            and self.standard == ""
            and self.definition_setting == ""
            and self.rule_full_name == ""
        ):
            elements = self.rule_uid.split(":")

            if len(elements) < 4:
                raise ValueError(
                    "Not enough elements to parse Rule UID. This should follow pattern described at https://github.com/asam-ev/qc-framework/blob/main/doc/manual/rule_uid_schema.md"
                )

            self.emanating_entity = elements[0]
            self.standard = elements[1]
            self.definition_setting = elements[2]
            self.rule_full_name = elements[3]

        return self

    @model_validator(mode="after")
    def check_any_empty(self) -> Any:
        """
        Validates if any field is empty after initialization. No field should
        be leave empty after a successful initialization happens.
        """
        if self.rule_uid == "":
            raise ValueError("Empty initialization of rule_uid")
        if self.emanating_entity == "":
            raise ValueError("Empty initialization of emanating_entity")
        if self.standard == "":
            raise ValueError("Empty initialization of standard")
        if self.definition_setting == "":
            raise ValueError("Empty initialization of definition_setting")
        if self.rule_full_name == "":
            raise ValueError("Empty initialization of rule_full_name")

        return self


class DomainSpecificInfoType(
    BaseXmlModel,
    tag="DomainSpecificInfo",
):
    name: str = attr(name="name")


class IssueType(
    BaseXmlModel,
    arbitrary_types_allowed=True,
):
    locations: List[LocationType] = element(tag="Locations", default=[])
    issue_id: int = attr(name="issueId")
    description: str = attr(name="description")
    level: IssueSeverity = attr(name="level")
    rule_uid: str = attr(
        name="ruleUID",
        default="",
        pattern=r"^((\w+(\.\w+)+)):(([a-z]+)):(([0-9]+(\.[0-9]+)+)):((([a-z][\w_]*)\.)*)([a-z][\w_]*)$",
    )
    # Raw is defined here to enable parsing of "any" XML tag inside the domain
    # specific information. It is linked to the DomainSpecificInfoType model
    # to enforce the attributes.
    # Linked Issue: https://github.com/dapper91/pydantic-xml/issues/100
    domain_specific_info: List[etree._Element] = element(
        tag="DomainSpecificInfo", default=[], excluded=True
    )


class MetadataType(BaseXmlModel):
    key: str = attr(name="key")
    value: str = attr(name="value")
    description: str = attr(name="description")


class StatusType(str, enum.Enum):
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


class CheckerType(BaseXmlModel, validate_assignment=True, search_mode="unordered"):
    params: List[ParamType] = element(tag="Param", default=[])
    addressed_rule: List[RuleType] = element(tag="AddressedRule", default=[])
    issues: List[IssueType] = element(tag="Issue", default=[])
    metadata: List[MetadataType] = element(tag="Metadata", default=[])
    status: StatusType = attr(name="status", default=None)
    checker_id: str = attr(name="checkerId")
    description: str = attr(name="description")
    summary: str = attr(name="summary")

    @model_validator(mode="after")
    def check_issue_ruleUID_matches_addressed_rules(self) -> Any:
        if len(self.issues):
            addressed_rule_uids: Set[int] = set()

            for addressed_rule in self.addressed_rule:
                addressed_rule_uids.add(addressed_rule.rule_uid)

            for issue in self.issues:
                if issue.rule_uid not in addressed_rule_uids:
                    raise ValueError(
                        f"Issue Rule UID '{issue.rule_uid}' does not match addressed rules UIDs {list(addressed_rule_uids)}"
                    )
        return self

    @model_validator(mode="after")
    def check_skipped_status_containing_issues(self) -> Any:
        if self.status == StatusType.SKIPPED and len(self.issues) > 0:
            raise ValueError(
                f"{self.checker_id}\nCheckers with skipped status cannot contain issues. Issues found: {len(self.issues)}"
            )
        return self


class CheckerBundleType(BaseXmlModel, search_mode="unordered"):
    params: List[ParamType] = element(tag="Param", default=[])
    checkers: List[CheckerType] = element(tag="Checker", default=[])
    build_date: str = attr(name="build_date")
    description: str = attr(name="description")
    name: str = attr(name="name")
    version: str = attr(name="version")
    summary: str = attr(name="summary")


class CheckerResults(BaseXmlModel, tag="CheckerResults"):
    checker_bundles: List[CheckerBundleType] = element(tag="CheckerBundle", default=[])
    version: str = attr(name="version")
