# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Union
from .models import report

REPORT_OUTPUT_FORMAT = "xqar"
DEFAULT_REPORT_VERSION = "0.0.1"


class Report:
    def __init__(
        self,
    ):
        self._report_results: Union[None, report.CheckerResults] = None

    def load_from_file(self, xml_file_path: str, override: bool = False) -> None:
        if self._report_results is not None and not override:
            raise RuntimeError(
                "Report already contains data, to re-load it please set the override=True"
            )

        with open(xml_file_path, "rb") as report_xml_file:
            xml_text = report_xml_file.read()
            self._report_results = report.CheckerResults.from_xml(xml_text)

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
            )
            report_xml_file.write(xml_text)

    def set_results_version(self, version: str) -> None:
        if self._report_results is None:
            self._report_results = report.CheckerBundleType(version=version)
        else:
            self._report_results.version = version

    def _get_bundle_by_name(self, bundle_name: str) -> report.CheckerBundleType:
        if self._report_results is None:
            raise RuntimeError(
                "Report not initialized. Initialize the report first by registering the version or a checker bundle."
            )

        bundle = next(
            (
                bundle
                for bundle in self._report_results.checker_bundles
                if bundle.name == bundle_name
            ),
            None,
        )

        if bundle is None:
            raise RuntimeError(
                f"Bundle not found. The specified {bundle_name} does not exist on the report. Register the bundle first."
            )

        return bundle

    def _get_checker_by_checker_id_from_bundle(
        self, bundle: report.CheckerBundleType, checker_id: str
    ) -> report.CheckerType:
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

    def _get_issue_by_id_from_checker(
        self, checker: report.CheckerType, issue_id: int
    ) -> report.IssueType:
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
        bundle = report.CheckerBundleType(
            build_date=build_date,
            description=description,
            name=name,
            version=version,
            summary=summary,
        )

        if self._report_results is None:
            self._report_results = report.CheckerResults(version=DEFAULT_REPORT_VERSION)

        self._report_results.checker_bundles.append(bundle)

    def register_checker_to_bundle(
        self, bundle_name: str, checker_id: str, description: str, summary: str
    ) -> None:

        checker = report.CheckerType(
            checker_id=checker_id, description=description, summary=summary
        )

        bundle = self._get_bundle_by_name(bundle_name=bundle_name)

        bundle.checkers.append(checker)

    def register_issue_to_checker(
        self,
        bundle_name: str,
        checker_id: str,
        issue_id: int,
        description: str,
        level: int,
    ) -> None:
        issue = report.IssueType(
            issue_id=issue_id, description=description, level=level
        )

        bundle = self._get_bundle_by_name(bundle_name=bundle_name)

        checker = self._get_checker_by_checker_id_from_bundle(
            bundle=bundle, checker_id=checker_id
        )

        checker.issues.append(issue)

    def add_file_location_to_issue(
        self,
        bundle_name: str,
        checker_id: str,
        issue_id: int,
        row: int,
        column: int,
        file_type: str,
        description: str,
    ) -> None:
        file_location = report.FileLocationType(
            row=row,
            column=column,
            file_type=file_type,
        )

        bundle = self._get_bundle_by_name(bundle_name=bundle_name)

        checker = self._get_checker_by_checker_id_from_bundle(
            bundle=bundle, checker_id=checker_id
        )
        issue = self._get_issue_by_id_from_checker(checker=checker, issue_id=issue_id)

        issue.locations.append(
            report.LocationType(file_location=[file_location], description=description)
        )

    def add_xml_location_to_issue(
        self,
        bundle_name: str,
        checker_id: str,
        issue_id: int,
        xpath: str,
    ) -> None:
        xml_location = report.XMLLocationType(xpath=xpath)

        bundle = self._get_bundle_by_name(bundle_name=bundle_name)

        checker = self._get_checker_by_checker_id_from_bundle(
            bundle=bundle, checker_id=checker_id
        )
        issue = self._get_issue_by_id_from_checker(checker=checker, issue_id=issue_id)

        issue.locations.append(report.LocationType(xml_location=[xml_location]))

    # TODO: Add get methods for Report
