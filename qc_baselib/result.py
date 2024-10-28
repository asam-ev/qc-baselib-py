# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging

from copy import deepcopy
from dataclasses import dataclass
from typing import Union, List, Set, Optional
from lxml import etree
from datetime import datetime

from qc_baselib import Configuration
from .models import IssueSeverity, StatusType, result, common


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
        description="Example checker bundle",
        version="0.0.1",
    )

    result.write_to_file("testResults.xqar")
    ```

    It allow users to read result reports by allowing them
    to load data files in memory and get attributes from it.

    ## Example
    ```python
    result = Result()

    result.load_from_file(RESULT_FILE_PATH)

    version = result.get_result_version()
    ```

    For more information regarding the results report XSD schema you can check
    [here](https://github.com/asam-ev/qc-framework/blob/main/doc/schema/xqar_report_format.xsd)

    """

    def __init__(
        self,
    ):
        self._report_results: Optional[result.CheckerResults] = None
        self._id_manager = IDManager()

    def load_from_file(self, xml_file_path: str, override: bool = False) -> None:
        if self._report_results is not None and not override:
            raise RuntimeError(
                "Report already contains data, to re-load it please set the override=True"
            )

        with open(xml_file_path, "rb") as report_xml_file:
            xml_text = report_xml_file.read()
            self._report_results = result.CheckerResults.from_xml(xml_text)

    def write_to_file(self, xml_output_file_path: str, generate_summary=False) -> None:
        """
        generate_summary : bool
            Automatically generate a summary for each checker and checker bundle.
            The generated summary will be appended to the current summary.
        """
        if self._report_results is None:
            raise RuntimeError(
                "Report dump with empty report, the report needs to be loaded first"
            )

        if generate_summary:
            self._generate_checker_bundle_summary()
            self._generate_checker_summary()

        with open(xml_output_file_path, "wb") as report_xml_file:
            xml_text = self._report_results.to_xml(
                pretty_print=True,
                xml_declaration=True,
                standalone=False,
                encoding="UTF-8",
                skip_empty=True,
            )
            report_xml_file.write(xml_text)

    def write_markdown_doc(self, markdown_file_path: str) -> None:
        if self._report_results is None:
            raise RuntimeError(
                "Report documentation dump with empty report, the report needs to be loaded first"
            )

        full_text = """
            This is the automatically generated documentation.
            The lists of checkers and addressed rules were exported from the
            information registered in the Result object for a particular run.
            Therefore, some checkers and addressed rules might be missing if
            they are not registered in that particular run. Double check with
            the implementation before using this generated documentation.\n\n"""

        for bundle in self._report_results.checker_bundles:
            bundle_text = ""
            bundle_text += f"# Checker bundle: {bundle.name}\n\n"
            bundle_text += f"* Build version:  {bundle.version}\n"
            bundle_text += f"* Description:    {bundle.description}\n"

            bundle_text += "\n"
            bundle_text += f"## Parameters\n\n"
            param_text = ""
            for param in bundle.params:
                param_text += f"* {param.name} \n"

            if len(param_text) == 0:
                param_text += f"* None\n"

            bundle_text += param_text

            bundle_text += "\n"
            bundle_text += f"## Checkers\n"
            checker_text = ""
            for checker in bundle.checkers:
                checker_text += "\n"
                checker_text += f"### {checker.checker_id}\n\n"
                checker_text += f"* Description: {checker.description}\n"

                checker_text += f"* Addressed rules:\n"
                rule_text = ""
                for rule in checker.addressed_rule:
                    rule_text += f"  * {rule.rule_uid}\n"

                if len(rule_text) == 0:
                    rule_text += f"  * None"

                checker_text += rule_text

            if len(checker_text) == 0:
                checker_text += f"* None"

            bundle_text += checker_text

            full_text += bundle_text

        with open(markdown_file_path, "wb") as doc_file:
            doc_file.write(full_text.encode())

    def set_result_version(self, version: str) -> None:
        if self._report_results is None:
            self.version = version
            self._report_results = result.CheckerBundleType(version=version)
        else:
            self._report_results.version = version

    def _generate_checker_bundle_summary(self) -> None:
        for bundle in self._report_results.checker_bundles:
            number_of_checkers = 0
            number_of_completed_checkers = 0
            number_of_skipped_checkers = 0
            number_of_error_checkers = 0
            number_of_no_status_checkers = 0

            for checker in bundle.checkers:
                number_of_checkers += 1
                if checker.status == StatusType.COMPLETED:
                    number_of_completed_checkers += 1
                elif checker.status == StatusType.SKIPPED:
                    number_of_skipped_checkers += 1
                elif checker.status == StatusType.ERROR:
                    number_of_error_checkers += 1
                else:
                    number_of_no_status_checkers += 1

            summary = (
                f"{number_of_checkers} checker(s) are executed. "
                f"{number_of_completed_checkers} checker(s) are completed. {number_of_skipped_checkers} checker(s) are skipped. "
                f"{number_of_error_checkers} checker(s) have internal error and {number_of_no_status_checkers} checker(s) do not contain status."
            )

            if bundle.summary == "":
                bundle.summary = summary
            else:
                bundle.summary += f" {summary}"

    def _generate_checker_summary(self) -> None:
        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                number_of_issues = len(checker.issues)

                summary = f"{number_of_issues} issue(s) are found."

                if checker.summary == "":
                    checker.summary = summary
                else:
                    checker.summary += f" {summary}"

    def add_checker_bundle_summary(
        self, checker_bundle_name: str, content: str
    ) -> None:
        """
        Add content to the existing summary of a checker bundle.
        The content will be appended to the current summary.
        """
        bundle = self._get_checker_bundle(checker_bundle_name)
        if bundle.summary == "":
            bundle.summary = content
        else:
            bundle.summary += f" {content}"

    def add_checker_summary(
        self, checker_bundle_name: str, checker_id: str, content: str
    ) -> None:
        """
        Add content to the existing summary of a checker.
        The content will be appended to the current summary.
        """
        bundle = self._get_checker_bundle(checker_bundle_name)
        checker = self._get_checker(bundle, checker_id)
        if checker.summary == "":
            checker.summary = content
        else:
            checker.summary += f" {content}"

    def _get_checker_bundle_without_error(
        self, checker_bundle_name: str
    ) -> Optional[result.CheckerBundleType]:
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

        return bundle

    def _get_checker_bundle(self, checker_bundle_name: str) -> result.CheckerBundleType:
        bundle = self._get_checker_bundle_without_error(checker_bundle_name)

        if bundle is None:
            raise RuntimeError(
                f"Bundle not found. The specified {checker_bundle_name} does not exist on the report. Register the bundle first."
            )

        return bundle

    def _get_checker_without_error(
        self, bundle: result.CheckerBundleType, checker_id: str
    ) -> Optional[result.CheckerType]:
        checker = next(
            (
                checker
                for checker in bundle.checkers
                if checker.checker_id == checker_id
            ),
            None,
        )

        return checker

    def _get_checker(
        self, bundle: result.CheckerBundleType, checker_id: str
    ) -> result.CheckerType:
        checker = self._get_checker_without_error(bundle, checker_id)

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
        self,
        description: str,
        name: str,
        version: str,
        build_date: Optional[str] = None,
        summary: str = "",
    ) -> None:
        bundle = result.CheckerBundleType(
            build_date=(
                build_date
                if build_date is not None
                else datetime.today().strftime("%Y-%m-%d")
            ),
            description=description,
            name=name,
            version=version,
            summary=summary,
        )

        if self._report_results is None:
            self._report_results = result.CheckerResults(version=DEFAULT_REPORT_VERSION)

        for existing_bundle in self._report_results.checker_bundles:
            if existing_bundle.name == name:
                raise RuntimeError(
                    f"Checker bundle with name {name} is already registered to results"
                )

        self._report_results.checker_bundles.append(bundle)

    def register_checker(
        self,
        checker_bundle_name: str,
        checker_id: str,
        description: str,
        summary: str = "",
    ) -> None:

        checker = result.CheckerType(
            checker_id=checker_id, description=description, summary=summary
        )

        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        for existing_checker in bundle.checkers:
            if existing_checker.checker_id == checker_id:
                raise RuntimeError(
                    f"Checker with id {checker_id} is already registered to bundle {bundle.name}"
                )

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

        number_of_addressed_rules = len(checker.addressed_rule)
        if number_of_addressed_rules > 1:
            logging.warning(
                f"There are {number_of_addressed_rules} rules registered to the check"
                f" {checker_id}. A check should address exactly one rule, unless there"
                " is a strong reason not to. See the following document for more"
                " information:"
                " https://github.com/asam-ev/qc-framework/blob/main/doc/manual/checker_library.md#check-characteristics"
            )

        return rule.rule_uid

    def register_rule_by_uid(
        self,
        checker_bundle_name: str,
        checker_id: str,
        rule_uid: str,
    ) -> None:
        """
        Rule uid will be registered to checker.

        Rule uid needs to follow the proper schema, more information at:
        https://github.com/asam-ev/qc-framework/blob/main/doc/manual/rule_uid_schema.md
        """

        splitted_uid = rule_uid.split(":")

        if len(splitted_uid) < 4:
            raise RuntimeError(
                f"Invalid rule uid: {rule_uid}. The uid should be composed by 4 entities separated by ':'."
            )

        self.register_rule(
            checker_bundle_name=checker_bundle_name,
            checker_id=checker_id,
            emanating_entity=splitted_uid[0],
            standard=splitted_uid[1],
            definition_setting=splitted_uid[2],
            rule_full_name=splitted_uid[3],
        )

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
        self, checker_bundle_name: str, checker_id: str, status: StatusType
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

    def has_issue_in_rules(self, rule_uid_set: Set[str]) -> bool:
        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                for issue in checker.issues:
                    if issue.rule_uid in rule_uid_set:
                        return True

        return False

    def has_issue_in_checkers(self, check_id_set: Set[str]) -> bool:
        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                if checker.checker_id in check_id_set and len(checker.issues) > 0:
                    return True

        return False

    def all_checkers_completed_without_issue(self, check_id_set: Set[str]) -> bool:
        checker_id_map = dict()
        for checker_id in check_id_set:
            checker_id_map[checker_id] = False

        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                if (
                    checker.checker_id in check_id_set
                    and checker.status == StatusType.COMPLETED
                    and len(checker.issues) == 0
                ):
                    checker_id_map[checker.checker_id] = True

        result = True

        for _, checker_result in checker_id_map.items():
            result = result and checker_result

        return result

    def get_checker_status(self, checker_id: str) -> Optional[StatusType]:
        """
        Return None if the checker is not found.
        """
        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                if checker.checker_id == checker_id:
                    return checker.status

        return None

    def all_checkers_completed(self) -> bool:
        for bundle in self._report_results.checker_bundles:
            for checker in bundle.checkers:
                if checker.status != StatusType.COMPLETED:
                    return False

        return True

    def add_param_to_checker_bundle(
        self, checker_bundle_name: str, name: str, value: Union[str, int, float]
    ) -> None:
        bundle = self._get_checker_bundle(checker_bundle_name)
        for exiting_param in bundle.params:
            if exiting_param.name == name:
                raise RuntimeError(
                    f"Param with name {name} is already registered to bundle {checker_bundle_name}"
                )
        bundle.params.append(common.ParamType(name=name, value=value))

    def get_param_from_checker_bundle(
        self, checker_bundle_name: str, param_name: str
    ) -> Union[int, str, float, None]:
        bundle = self._get_checker_bundle(checker_bundle_name)

        if len(bundle.params) == 0:
            return None

        param = next(
            (param for param in bundle.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def add_param_to_checker(
        self,
        checker_bundle_name: str,
        checker_id: str,
        name: str,
        value: Union[str, int, float],
    ) -> None:
        bundle = self._get_checker_bundle(checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)
        for exiting_param in checker.params:
            if exiting_param.name == name:
                raise RuntimeError(
                    f"Param with name {name} is already registered to checker {checker_id} on bundle {checker_bundle_name}"
                )
        checker.params.append(common.ParamType(name=name, value=value))

    def get_param_from_checker(
        self, checker_bundle_name: str, checker_id: str, param_name: str
    ) -> Union[int, str, float, None]:
        bundle = self._get_checker_bundle(checker_bundle_name)
        checker = self._get_checker(bundle=bundle, checker_id=checker_id)

        if len(checker.params) == 0:
            return None

        param = next(
            (param for param in checker.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def copy_param_from_config(self, config: Configuration) -> None:
        # Inject global Configuration parameters to Result checker bundles
        for param_name, param_value in config.get_all_global_config_param().items():
            result_checker_bundles = self._report_results.checker_bundles
            for bundle in result_checker_bundles:
                bundle.params.append(
                    common.ParamType(name=param_name, value=param_value)
                )

        # Copy Configuration checker bundle and checker parameters to Result
        for config_bundle in config.get_all_checker_bundles():
            result_bundle = self._get_checker_bundle_without_error(
                checker_bundle_name=config_bundle.application
            )

            if result_bundle is None:
                continue

            for param in config_bundle.params:
                result_bundle.params.append(
                    common.ParamType(name=param.name, value=param.value)
                )

            for config_checker in config_bundle.checkers:
                result_checker = self._get_checker_without_error(
                    bundle=result_bundle,
                    checker_id=config_checker.checker_id,
                )

                if result_checker is None:
                    continue

                for param in config_checker.params:
                    result_checker.params.append(
                        common.ParamType(name=param.name, value=param.value)
                    )
