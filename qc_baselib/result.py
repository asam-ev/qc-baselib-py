# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from copy import deepcopy
from dataclasses import dataclass
from typing import Union, List, Dict, Any
from lxml import etree
from .models import IssueSeverity, result

REPORT_OUTPUT_FORMAT = "xqar"
DEFAULT_REPORT_VERSION = "0.0.1"


@dataclass
class DomainSpecificInfoContent:
    name: str
    content: List[etree._Element]


class IDManager:
    _id = -1

    def get_next_free_id(self):
        self._id += 1
        return self._id


class Result:
    """
    Quality framework `Result` schema class.

    This class is responsible for manipulating results reports elements in the
    framework workflow.

    It allows uses to write result reports by allowing them to populate the
    instance of it and write to a file.

    ## Example
    ```python
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.write_to_file("testResults.xqar")
    ```

    It allow users to read result reports by allowing them
    to load data files in memory and get attributes from it.

    ## Example
    ```python
    result = Result()

    result.load_from_file(RESULT_FILE_PATH)

    version = result.get_version()
    ```

    For more information regarding the results report XSD schema you can check
    [here](https://github.com/asam-ev/qc-framework/blob/develop/doc/schema/xqar_report_format.xsd)

    """

    def __init__(
        self,
    ):
        self._report_results: Union[None, result.CheckerResults] = None
        self._id_manager = IDManager()

    def load_from_file(self, xml_file_path: str, override: bool = False) -> None:
        if self._report_results is not None and not override:
            raise RuntimeError(
                "Report already contains data, to re-load it please set the override=True"
            )

        with open(xml_file_path, "rb") as report_xml_file:
            xml_text = report_xml_file.read()
            self._report_results = result.CheckerResults.from_xml(xml_text)

    def write_to_file(self, xml_output_file_path: str) -> None:
        if self._report_results is None:
            raise RuntimeError(
                "Report dump with empty report, the report needs to be loaded first"
            )
        with open(xml_output_file_path, "wb") as report_xml_file:
            xml_text = self._report_results.to_xml(
                pretty_print=True,
                xml_declaration=True,
                standalone=False,
                encoding="UTF-8",
                skip_empty=True,
            )
            report_xml_file.write(xml_text)

    def set_result_version(self, version: str) -> None:
        if self._report_results is None:
            self.version = version
            self._report_results = result.CheckerBundleType(version=version)
        else:
            self._report_results.version = version

    def _get_checker_bundle(self, checker_bundle_name: str) -> result.CheckerBundleType:
        if self._report_results is None:
            raise RuntimeError(
                "Report not initialized. Initialize the report first by registering the version or a checker bundle."
            )

        bundle = next(
            (
                bundle
                for bundle in self._report_results.checker_bundles
                if bundle.name == checker_bundle_name
            ),
            None,
        )

        if bundle is None:
            raise RuntimeError(
                f"Bundle not found. The specified {checker_bundle_name} does not exist on the report. Register the bundle first."
            )

        return bundle

    def _get_checker(
        self, bundle: result.CheckerBundleType, checker_id: str
    ) -> result.CheckerType:
        checker = next(
            (
                checker
                for checker in bundle.checkers
                if checker.checker_id == checker_id
            ),
            None,
        )

        if checker is None:
            raise RuntimeError(
                f"Checker not found. The specified {checker_id} does not exist on the report. Register the checker first."
            )

        return checker

    def _get_issue(
        self, checker: result.CheckerType, issue_id: int
    ) -> result.IssueType:
        issue = next(
            (issue for issue in checker.issues if issue.issue_id == issue_id),
            None,
        )

        if issue is None:
            raise RuntimeError(
                f"Issue not found. The specified {issue_id} does not exist on the report. Register the issue first."
            )

        return issue

    def register_checker_bundle(
        self, build_date: str, description: str, name: str, version: str, summary: str
    ) -> None:
        bundle = result.CheckerBundleType(
            build_date=build_date,
            description=description,
            name=name,
            version=version,
            summary=summary,
        )

        if self._report_results is None:
            self._report_results = result.CheckerResults(version=DEFAULT_REPORT_VERSION)

        self._report_results.checker_bundles.append(bundle)

    def register_checker(
        self,
        checker_bundle_name: str,
        checker_id: str,
        description: str,
        summary: str,
    ) -> None:

        checker = result.CheckerType(
            checker_id=checker_id, description=description, summary=summary
        )

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        bundle.checkers.append(checker)

    def register_rule(
        self,
        checker_bundle_name: str,
        checker_id: str,
        emanating_entity: str,
        standard: str,
        definition_setting: str,
        rule_full_name: str,
    ) -> str:
        """
        Rule will be registered to checker and the generated rule uid will be
        returned.
        """

        rule = result.RuleType(
            emanating_entity=emanating_entity,
            standard=standard,
            definition_setting=definition_setting,
            rule_full_name=rule_full_name,
        )

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        checker.addressed_rule.append(rule)

        return rule.rule_uid

    def register_issue(
        self,
        checker_bundle_name: str,
        checker_id: str,
        description: str,
        level: IssueSeverity,
        rule_uid: str,
    ) -> int:
        """
        Issue will be registered to checker and the generated issue id will be
        returned.
        """
        issue_id = self._id_manager.get_next_free_id()

        issue = result.IssueType(
            issue_id=issue_id, description=description, level=level, rule_uid=rule_uid
        )

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        checker = self._get_checker(bundle=bundle, checker_id=checker_id)

        checker.issues.append(issue)

        # Validation need to be triggered to check if no schema relation was
        # violated by the new issue addition.
        result.CheckerType.model_validate(checker)

        return issue_id

    def add_file_location(
        self,
        checker_bundle_name: str,
        checker_id: str,
        issue_id: int,
        row: int,
        column: int,
        description: str,
    ) -> None:
        file_location = result.FileLocationType(
            row=row,
            column=column,
        )

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        issue = self._get_issue(checker=checker, issue_id=issue_id)

        issue.locations.append(
            result.LocationType(file_location=[file_location], description=description)
        )

    def add_xml_location(
        self,
        checker_bundle_name: str,
        checker_id: str,
        issue_id: int,
        xpath: Union[str, List[str]],
        description: str,
    ) -> None:
        xml_locations = []

        if type(xpath) == str:
            xml_locations.append(result.XMLLocationType(xpath=xpath))
        elif type(xpath) == list:
            for path in xpath:
                xml_locations.append(result.XMLLocationType(xpath=path))

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        issue = self._get_issue(checker=checker, issue_id=issue_id)

        issue.locations.append(
            result.LocationType(xml_location=xml_locations, description=description)
        )

    def add_inertial_location(
        self,
        checker_bundle_name: str,
        checker_id: str,
        issue_id: int,
        x: float,
        y: float,
        z: float,
        description: str,
    ) -> None:
        inertial_location = result.InertialLocationType(x=x, y=y, z=z)

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        issue = self._get_issue(checker=checker, issue_id=issue_id)

        issue.locations.append(
            result.LocationType(
                inertial_location=[inertial_location], description=description
            )
        )

    def add_domain_specific_info(
        self,
        checker_bundle_name: str,
        checker_id: str,
        issue_id: int,
        domain_specific_info_name: str,
        xml_info: List[etree._Element],
    ) -> None:
        """
        Adds named domain specific information.

        The domain specific information contains a name and a list of relevant
        xml elements.
        """
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        issue = self._get_issue(checker=checker, issue_id=issue_id)

        domain_specific_tag = etree.Element(
            "DomainSpecificInfo", attrib={"name": domain_specific_info_name}
        )

        for xml_info_element in xml_info:
            xml_info_to_append = deepcopy(xml_info_element)
            domain_specific_tag.append(xml_info_to_append)

        issue.domain_specific_info.append(domain_specific_tag)

    def set_checker_status(
        self, checker_bundle_name: str, checker_id: str, status: result.StatusType
    ) -> None:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        checker.status = status
        result.CheckerType.model_validate(checker)

    def get_result_version(self) -> str:
        return self._report_results.version

    def get_checker_bundle_names(self) -> List[str]:
        bundles_names = []

        for bundle in self._report_results.checker_bundles:
            bundles_names.append(bundle.name)

        return bundles_names

    def get_checker_ids(self, checker_bundle_name: str) -> List[str]:
        checkers_ids = []

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        if bundle is None:
            return checkers_ids

        for checker in bundle.checkers:
            checkers_ids.append(checker.checker_id)

        return checkers_ids

    def get_issue_ids(self, checker_bundle_name: str, checker_id: str) -> List[int]:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)

        issues_ids = []

        for issue in checker.issues:
            issues_ids.append(issue.issue_id)

        return issues_ids

    def get_checker_bundle_results(self) -> List[result.CheckerBundleType]:
        return self._report_results.checker_bundles

    def get_checker_bundle_result(
        self, checker_bundle_name: str
    ) -> result.CheckerBundleType:
        return self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

    def get_checker_results(self, checker_bundle_name: str) -> List[result.CheckerType]:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        return bundle.checkers

    def get_checker_result(
        self, checker_bundle_name: str, checker_id: str
    ) -> result.CheckerType:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        return self._get_checker(bundle=bundle, checker_id=checker_id)

    def get_issues(
        self, checker_bundle_name: str, checker_id: str
    ) -> List[result.IssueType]:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        return checker.issues

    def get_checker_issue_count(self, checker_bundle_name: str, checker_id: str) -> int:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        return len(checker.issues)

    def get_checker_bundle_issue_count(self, checker_bundle_name: str) -> int:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        issue_count = 0

        for checker in bundle.checkers:
            issue_count += len(checker.issues)

        return issue_count

    def get_issue_count(self) -> int:
        checker_bundle_names = self.get_checker_bundle_names()

        issue_count = 0
        for checker_bundle_name in checker_bundle_names:
            issue_count += self.get_checker_bundle_issue_count(
                checker_bundle_name=checker_bundle_name
            )

        return issue_count

    def get_domain_specific_info(
        self,
        checker_bundle_name: str,
        checker_id: str,
        issue_id: int,
    ) -> List[DomainSpecificInfoContent]:
        """
        Returns a list of named domain specific information.

        Each domain specific information content contains a name and a list of
        relevant xml elements.
        """
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        issue = self._get_issue(checker=checker, issue_id=issue_id)

        domain_specific_list = []

        for domain_specific_info in issue.domain_specific_info:
            attrib = domain_specific_info.attrib
            info_dict = DomainSpecificInfoContent(
                name=attrib["name"], content=domain_specific_info.getchildren()
            )

            domain_specific_list.append(info_dict)

        return domain_specific_list

    def get_issues_by_rule_uid(self, rule_uid: str) -> List[result.IssueType]:
        rule_issues: List[result.IssueType] = []

        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                for issue in checker.issues:
                    if issue.rule_uid == rule_uid:
                        rule_issues.append(issue)

        return rule_issues
