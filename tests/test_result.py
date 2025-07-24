# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import pytest
from lxml import etree
from pydantic_core import ValidationError
from datetime import datetime
from qc_baselib.models import result
from qc_baselib import Result, IssueSeverity, StatusType, Configuration


DEMO_REPORT_PATH = "tests/data/demo_checker_bundle.xqar"
EXTENDED_DEMO_REPORT_PATH = "tests/data/demo_checker_bundle_extended.xqar"
EXAMPLE_OUTPUT_REPORT_PATH = "tests/data/result_test_output.xqar"
EXAMPLE_OUTPUT_MARKDOWN_DOC_PATH = "tests/data/result_markdown_docs.md"
TEST_REPORT_OUTPUT_PATH = "tests/result_test_output.xqar"
TEST_MARKDOWN_DOC_OUTPUT_PATH = "tests/result_markdown_docs.md"


@pytest.fixture
def loaded_result() -> Result:
    result = Result()
    result.load_from_file(DEMO_REPORT_PATH)
    return result


@pytest.fixture
def loaded_extended_result() -> Result:
    result = Result()
    result.load_from_file(EXTENDED_DEMO_REPORT_PATH)
    return result


def test_load_result_from_file() -> None:
    result = Result()
    result.load_from_file(DEMO_REPORT_PATH)
    assert len(result._report_results.to_xml()) > 0


def test_load_result_from_extended_file() -> None:
    result = Result()
    result.load_from_file(EXTENDED_DEMO_REPORT_PATH)
    assert len(result._report_results.to_xml()) > 0


def test_result_write() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers.",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation.",
    )

    rule_uid = result.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    result.add_file_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        row=1,
        column=0,
        description="Location for issue",
    )
    result.add_xml_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        xpath="/foo/test/path",
        description="Location for issue",
    )
    result.add_xml_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        xpath=["/foo/test/path", "/bar/test/path"],
        description="Location for issue with list",
    )
    result.add_inertial_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        x=1.0,
        y=2.0,
        z=3.0,
        description="Location for issue",
    )

    result.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    result.add_checker_bundle_summary(
        checker_bundle_name="TestBundle", content="Extra summary for checker bundle."
    )
    result.add_checker_summary(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        content="Extra summary for checker.",
    )

    result.write_to_file(TEST_REPORT_OUTPUT_PATH, generate_summary=True)

    example_xml_text = ""
    output_xml_text = ""
    with open(EXAMPLE_OUTPUT_REPORT_PATH, "r") as result_xml_file:
        example_xml_text = result_xml_file.read()
    with open(TEST_REPORT_OUTPUT_PATH, "r") as result_xml_file:
        output_xml_text = result_xml_file.read()

    assert output_xml_text == example_xml_text

    os.remove(TEST_REPORT_OUTPUT_PATH)


def test_result_bundles_load(loaded_result: Result):
    bundles_names = loaded_result.get_checker_bundle_names()

    assert len(bundles_names) == 1

    bundles = loaded_result.get_checker_bundle_results()

    assert len(bundles) == 1
    assert bundles[0].name == "DemoCheckerBundle"


def test_result_checkers_load(loaded_result: Result):
    bundle_checkers = loaded_result.get_checker_results(
        checker_bundle_name="DemoCheckerBundle"
    )

    assert len(bundle_checkers) == 1
    assert bundle_checkers[0].checker_id == "exampleChecker"

    example_checker_results = loaded_result.get_checker_result(
        checker_bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
    )

    assert example_checker_results.checker_id == "exampleChecker"


def test_result_issues_load(loaded_result: Result):
    issues = loaded_result.get_issues(
        checker_bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
    )

    assert issues[0].description == "This is an information from the demo usecase"
    assert issues[0].issue_id == 0
    assert issues[0].level == IssueSeverity.INFORMATION


def test_result_issues_count(loaded_result: Result):
    assert loaded_result.get_issue_count() == 1
    assert (
        loaded_result.get_checker_bundle_issue_count(
            checker_bundle_name="DemoCheckerBundle"
        )
        == 1
    )
    assert (
        loaded_result.get_checker_issue_count(
            checker_bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
        )
        == 1
    )


def test_result_register_issue_id_generation() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid = result.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id_0 = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    issue_id_1 = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    assert issue_id_0 != issue_id_1
    assert issue_id_0 == issue_id_1 - 1


def test_create_issue_with_unregistered_rule_id() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    with pytest.raises(
        ValidationError,
        match=r".* Issue Rule UID 'test.com:qc:1.0.0:qwerty.qwerty' does not match addressed rules UIDs \[\].*",
    ) as exc_info:
        issue_id_0 = result.register_issue(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            description="Issue found at odr",
            level=IssueSeverity.INFORMATION,
            rule_uid="test.com:qc:1.0.0:qwerty.qwerty",
        )


def test_create_rule_id_validation() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    with pytest.raises(
        ValidationError,
        match=r".*\nemanating_entity\n.* String should match pattern .*",
    ) as exc_info:
        rule_uid = result.register_rule(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            emanating_entity="",
            standard="qc",
            definition_setting="1.0.0",
            rule_full_name="qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\nstandard\n.* String should match pattern .*",
    ) as exc_info:
        rule_uid = result.register_rule(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            emanating_entity="test.com",
            standard="",
            definition_setting="1.0.0",
            rule_full_name="qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\ndefinition_setting\n.* String should match pattern .*",
    ) as exc_info:
        rule_uid = result.register_rule(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            emanating_entity="test.com",
            standard="qc",
            definition_setting="",
            rule_full_name="qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\nrule_full_name\n.* String should match pattern .*",
    ) as exc_info:
        rule_uid = result.register_rule(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            emanating_entity="test.com",
            standard="qc",
            definition_setting="1.0.0",
            rule_full_name="",
        )


def test_set_checker_status_skipped_with_issues() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid = result.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id_0 = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    with pytest.raises(
        ValidationError,
        match=r".*\nCheckers with skipped status cannot contain issues\. .*",
    ) as exc_info:
        result.set_checker_status(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            status=StatusType.SKIPPED,
        )


def test_domain_specific_load(loaded_extended_result: Result):
    issue = (
        loaded_extended_result._report_results.checker_bundles[0].checkers[3].issues[0]
    )

    # Evaluate if loading of issues with domain elements is properly done
    assert len(issue.locations) == 1
    assert len(issue.domain_specific_info) == 2
    assert type(issue.domain_specific_info) == list
    assert type(issue.domain_specific_info[0]) == etree._Element


def test_domain_specific_info_add():
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid = result.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    xml_info = etree.Element("TestCustomTag", attrib={"test": "value"})
    xml_info.append(etree.Element("NestedCustomTag1", attrib={"test": "value1"}))
    xml_info.append(etree.Element("NestedCustomTag2", attrib={"test": "value2"}))

    result.add_xml_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        xpath="/foo/test/path",
        description="Location for issue",
    )

    result.add_domain_specific_info(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        domain_specific_info_name="TestSpecificInfo",
        xml_info=[xml_info],
    )

    result.add_file_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        row=1,
        column=0,
        description="Location for issue",
    )

    result.add_domain_specific_info(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        domain_specific_info_name="DebugInfo",
        xml_info=[xml_info, xml_info],
    )

    result.write_to_file(TEST_REPORT_OUTPUT_PATH)

    output_result = Result()
    output_result.load_from_file(TEST_REPORT_OUTPUT_PATH)

    domain_specific_xml_element = output_result.get_domain_specific_info(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
    )

    assert len(domain_specific_xml_element) == 2

    name = domain_specific_xml_element[0].name
    content = domain_specific_xml_element[0].content

    assert len(content) == 1
    assert type(name) == str
    assert name == "TestSpecificInfo"

    children_content = content[0]

    domain_specific_xml_text = (
        etree.tostring(
            children_content,
        )
        .decode("utf-8")
        .replace(" ", "")
        .replace("\n", "")
    )  # need to take out any whitespace or \n due to tree indentation

    xml_info_text = (
        etree.tostring(
            xml_info,
        )
        .decode("utf-8")
        .replace(" ", "")
        .replace("\n", "")
    )  # need to take out any whitespace or \n due to tree indentation

    assert domain_specific_xml_text == xml_info_text

    os.remove(TEST_REPORT_OUTPUT_PATH)


def test_get_issue_by_rule_uid() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid_1 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id = result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_1,
    )

    issue_id = result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr secondary",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_1,
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        description="Test checker 2",
        summary="Executed evaluation 2",
    )

    rule_uid_2 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        emanating_entity="new.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id = result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        description=f"Issue found at odr on rule uid {rule_uid_2}",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_2,
    )

    rule_uid_1_issues = result_report.get_issues_by_rule_uid(rule_uid_1)
    rule_uid_2_issues = result_report.get_issues_by_rule_uid(rule_uid_2)

    assert len(rule_uid_1_issues) == 2
    assert len(rule_uid_2_issues) == 1
    assert type(rule_uid_2_issues[0]) == result.IssueType
    assert (
        rule_uid_2_issues[0].description
        == f"Issue found at odr on rule uid {rule_uid_2}"
    )
    assert rule_uid_2_issues[0].level == IssueSeverity.INFORMATION


def test_markdown_docs_output():
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid = result.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="qwerty.qwerty",
    )

    issue_id = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    result.add_file_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        row=1,
        column=0,
        description="Location for issue",
    )

    result.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    result.write_markdown_doc(TEST_MARKDOWN_DOC_OUTPUT_PATH)

    example_md_text = ""
    output_md_text = ""
    with open(EXAMPLE_OUTPUT_MARKDOWN_DOC_PATH, "r") as md_file:
        example_md_text = md_file.read()
    with open(TEST_MARKDOWN_DOC_OUTPUT_PATH, "r") as md_file:
        output_md_text = md_file.read()

    assert output_md_text == example_md_text

    os.remove(TEST_MARKDOWN_DOC_OUTPUT_PATH)


def test_has_issue_in_rules() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid_1 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="first.rule",
    )

    result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_1,
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid_2 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="second.rule",
    )

    result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker2",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_2,
    )

    assert (
        result_report.has_issue_in_rules(
            {"test.com:qc:1.0.0:third.rule", "test.com:qc:1.0.0:fourth.rule"}
        )
        == False
    )

    assert (
        result_report.has_issue_in_rules(
            {"test.com:qc:1.0.0:first.rule", "test.com:qc:1.0.0:fourth.rule"}
        )
        == True
    )

    assert (
        result_report.has_issue_in_rules(
            {"test.com:qc:1.0.0:second.rule", "test.com:qc:1.0.0:fourth.rule"}
        )
        == True
    )

    assert result_report.has_issue_in_rules({}) == False


def test_has_issue_in_checkers() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    rule_uid_1 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="first.rule",
    )

    result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_1,
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="SecondChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="SecondChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="second.rule",
    )

    assert (
        result_report.has_issue_in_checkers({"SecondChecker", "ThirdChecker"}) == False
    )

    assert (
        result_report.has_issue_in_checkers({"FirstChecker", "SecondChecker"}) == True
    )

    assert result_report.has_issue_in_checkers({"FirstChecker", "ThirdChecker"}) == True

    assert result_report.has_issue_in_checkers({}) == False


def test_all_checkers_completed_without_issue() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        description="",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="SecondChecker",
        description="",
    )

    assert result_report.all_checkers_completed_without_issue() == False

    assert result_report.all_checkers_completed_without_issue({"ThirdChecker"}) == False

    assert (
        result_report.all_checkers_completed_without_issue(
            {"FirstChecker", "SecondChecker"}
        )
        == False
    )

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.all_checkers_completed_without_issue() == False
    assert result_report.all_checkers_completed_without_issue({"FirstChecker"}) == True
    assert (
        result_report.all_checkers_completed_without_issue(
            {"FirstChecker", "SecondChecker"}
        )
        == False
    )

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        status=StatusType.SKIPPED,
    )

    assert result_report.all_checkers_completed_without_issue() == False
    assert result_report.all_checkers_completed_without_issue({"FirstChecker"}) == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        status=StatusType.ERROR,
    )

    assert result_report.all_checkers_completed_without_issue() == False
    assert result_report.all_checkers_completed_without_issue({"FirstChecker"}) == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        status=StatusType.COMPLETED,
    )

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="SecondChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.all_checkers_completed_without_issue() == True
    assert (
        result_report.all_checkers_completed_without_issue(
            {"FirstChecker", "SecondChecker"}
        )
        == True
    )
    assert result_report.all_checkers_completed_without_issue({"ThirdChecker"}) == False

    rule_uid_1 = result_report.register_rule(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        emanating_entity="test.com",
        standard="qc",
        definition_setting="1.0.0",
        rule_full_name="first.rule",
    )

    result_report.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="FirstChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid_1,
    )

    assert result_report.all_checkers_completed_without_issue() == False
    assert (
        result_report.all_checkers_completed_without_issue(
            {"FirstChecker", "SecondChecker"}
        )
        == False
    )

    assert result_report.all_checkers_completed_without_issue({"FirstChecker"}) == False
    assert result_report.all_checkers_completed_without_issue({"SecondChecker"}) == True
    assert result_report.all_checkers_completed_without_issue({}) == True


def test_registration_without_summary() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
    )

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
    )

    assert True


def test_get_checker_status() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
    )

    assert result_report.get_checker_status("TestChecker") == None

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="",
    )

    assert result_report.get_checker_status("TestChecker") == None

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.get_checker_status("TestChecker") == StatusType.COMPLETED

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.SKIPPED,
    )

    assert result_report.get_checker_status("TestChecker") == StatusType.SKIPPED

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.ERROR,
    )

    assert result_report.get_checker_status("TestChecker") == StatusType.ERROR


def test_all_checkers_completed() -> None:
    result_report = Result()

    result_report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
    )

    assert result_report.all_checkers_completed() == True

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="",
    )

    assert result_report.all_checkers_completed() == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.all_checkers_completed() == True

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.SKIPPED,
    )

    assert result_report.all_checkers_completed() == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.ERROR,
    )

    assert result_report.all_checkers_completed() == False

    result_report.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="SecondTestChecker",
        description="",
    )

    assert result_report.all_checkers_completed() == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.all_checkers_completed() == False

    result_report.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="SecondTestChecker",
        status=StatusType.COMPLETED,
    )

    assert result_report.all_checkers_completed() == True


def test_add_get_param_to_checker_bundle() -> None:
    result = Result()
    result.register_checker_bundle(
        build_date="",
        description="",
        name="TestCheckerBundle",
        version="",
    )

    result.add_param_to_checker_bundle(
        checker_bundle_name="TestCheckerBundle", name="TestStrParam", value="TestStr"
    )
    result.add_param_to_checker_bundle(
        checker_bundle_name="TestCheckerBundle", name="TestIntParam", value=1
    )
    result.add_param_to_checker_bundle(
        checker_bundle_name="TestCheckerBundle", name="TestFloatParam", value=2.0
    )

    assert (
        result.get_param_from_checker_bundle(
            checker_bundle_name="TestCheckerBundle", param_name="TestStrParam"
        )
        == "TestStr"
    )
    assert (
        result.get_param_from_checker_bundle(
            checker_bundle_name="TestCheckerBundle", param_name="TestIntParam"
        )
        == 1
    )
    assert (
        result.get_param_from_checker_bundle(
            checker_bundle_name="TestCheckerBundle", param_name="TestFloatParam"
        )
        == 2.0
    )


def test_add_get_param_to_checker() -> None:
    result = Result()
    result.register_checker_bundle(
        build_date="",
        description="",
        name="TestCheckerBundle",
        version="",
    )
    result.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        description="",
    )

    result.add_param_to_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="TestStrParam",
        value="TestStr",
    )
    result.add_param_to_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="TestIntParam",
        value=1,
    )
    result.add_param_to_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="TestFloatParam",
        value=2.0,
    )

    assert (
        result.get_param_from_checker(
            checker_bundle_name="TestCheckerBundle",
            checker_id="TestChecker",
            param_name="TestStrParam",
        )
        == "TestStr"
    )
    assert (
        result.get_param_from_checker(
            checker_bundle_name="TestCheckerBundle",
            checker_id="TestChecker",
            param_name="TestIntParam",
        )
        == 1
    )
    assert (
        result.get_param_from_checker(
            checker_bundle_name="TestCheckerBundle",
            checker_id="TestChecker",
            param_name="TestFloatParam",
        )
        == 2.0
    )


def test_result_config_param_copy() -> None:
    config = Configuration()
    config.register_checker_bundle(checker_bundle_name="TestCheckerBundle")
    config.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        min_level=IssueSeverity.INFORMATION,
        max_level=IssueSeverity.ERROR,
    )

    config.set_config_param(
        name="testConfigParamStr",
        value="testValue",
    )
    config.set_config_param(
        name="testConfigParamInt",
        value=1,
    )
    config.set_config_param(
        name="testConfigParamFloat",
        value=2.0,
    )

    config.set_checker_bundle_param(
        checker_bundle_name="TestCheckerBundle",
        name="testConfigParamStr",
        value="testValue",
    )
    config.set_checker_bundle_param(
        checker_bundle_name="TestCheckerBundle",
        name="testConfigParamInt",
        value=1,
    )
    config.set_checker_bundle_param(
        checker_bundle_name="TestCheckerBundle",
        name="testConfigParamFloat",
        value=2.0,
    )

    config.set_checker_param(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="testConfigParamStr",
        value="testValue",
    )
    config.set_checker_param(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="testConfigParamInt",
        value=1,
    )
    config.set_checker_param(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="testConfigParamFloat",
        value=2.0,
    )

    config.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="FirstNonExistingTestChecker",
        min_level=IssueSeverity.INFORMATION,
        max_level=IssueSeverity.ERROR,
    )

    config.register_checker_bundle(checker_bundle_name="NonExistingTestCheckerBundle")
    config.register_checker(
        checker_bundle_name="NonExistingTestCheckerBundle",
        checker_id="SecondNonExistingTestChecker",
        min_level=IssueSeverity.INFORMATION,
        max_level=IssueSeverity.ERROR,
    )

    result = Result()
    result.register_checker_bundle(
        build_date="",
        description="",
        name="TestCheckerBundle",
        version="",
    )
    result.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        description="",
    )

    result.copy_param_from_config(config=config)

    test_bundle = result.get_checker_bundle_result(
        checker_bundle_name="TestCheckerBundle"
    )
    test_checker = result.get_checker_result(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
    )
    config_bundle = config._get_checker_bundle(checker_bundle_name="TestCheckerBundle")
    config_checker = next(
        (
            checker
            for checker in config_bundle.checkers
            if checker.checker_id == "TestChecker"
        ),
        None,
    )

    assert len(test_bundle.params) == len(config_bundle.params) + len(
        config._configuration.params
    )
    assert len(test_checker.params) == len(config_checker.params)

    assert test_bundle.params[0].name == config_bundle.params[0].name
    assert test_bundle.params[0].value == config_bundle.params[0].value

    assert test_checker.params[0].name == config_checker.params[0].name
    assert test_checker.params[0].value == config_checker.params[0].value


def test_registering_checker_bundle_twice() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        result_report = Result()
        bundle_name = "TestBundle"

        result_report.register_checker_bundle(
            name=bundle_name,
            build_date="2024-05-31",
            description="Example checker bundle",
            version="0.0.1",
            summary="Tested example checkers",
        )

        result_report.register_checker_bundle(
            name=bundle_name,
            build_date="2024-05-31",
            description="Example checker bundle",
            version="0.0.1",
            summary="Tested example checkers",
        )

    assert (
        f"Checker bundle with name {bundle_name} is already registered to results"
        in str(exc_info.value)
    )


def test_registering_checker_twice() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        result_report = Result()
        bundle_name = "TestBundle"
        checker_id = "TestChecker"

        result_report.register_checker_bundle(
            name=bundle_name,
            build_date="2024-05-31",
            description="Example checker bundle",
            version="0.0.1",
            summary="Tested example checkers",
        )

        result_report.register_checker(
            checker_bundle_name=bundle_name,
            checker_id=checker_id,
            description="Test checker",
            summary="Executed evaluation",
        )
        result_report.register_checker(
            checker_bundle_name=bundle_name,
            checker_id=checker_id,
            description="Test checker",
            summary="Executed evaluation",
        )

    assert (
        f"Checker with id {checker_id} is already registered to bundle {bundle_name}"
        in str(exc_info.value)
    )


def test_registering_checker_bundle_param_twice() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        result_report = Result()
        bundle_name = "TestBundle"
        param_name = "TestFloatParam"

        result_report.register_checker_bundle(
            name=bundle_name,
            build_date="2024-05-31",
            description="Example checker bundle",
            version="0.0.1",
            summary="Tested example checkers",
        )

        result_report.add_param_to_checker_bundle(
            checker_bundle_name=bundle_name,
            name=param_name,
            value=2.0,
        )
        result_report.add_param_to_checker_bundle(
            checker_bundle_name=bundle_name,
            name=param_name,
            value=2.0,
        )

    assert (
        f"Param with name {param_name} is already registered to bundle {bundle_name}"
        in str(exc_info.value)
    )


def test_registering_checker_param_twice() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        result_report = Result()
        bundle_name = "TestBundle"
        checker_id = "TestChecker"
        param_name = "TestFloatParam"

        result_report.register_checker_bundle(
            name=bundle_name,
            build_date="2024-05-31",
            description="Example checker bundle",
            version="0.0.1",
            summary="Tested example checkers",
        )

        result_report.register_checker(
            checker_bundle_name=bundle_name,
            checker_id=checker_id,
            description="Test checker",
            summary="Executed evaluation",
        )

        result_report.add_param_to_checker(
            checker_bundle_name=bundle_name,
            checker_id=checker_id,
            name=param_name,
            value=2.0,
        )
        result_report.add_param_to_checker(
            checker_bundle_name=bundle_name,
            checker_id=checker_id,
            name=param_name,
            value=2.0,
        )

    assert (
        f"Param with name {param_name} is already registered to checker {checker_id} on bundle {bundle_name}"
        in str(exc_info.value)
    )


def test_result_register_rule_by_uid() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers.",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation.",
    )

    result.register_rule_by_uid(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        rule_uid="test.com:qc:1.0.0:qwerty.qwerty",
    )

    bundle = result._get_checker_bundle(checker_bundle_name="TestBundle")

    checker = result._get_checker(bundle=bundle, checker_id="TestChecker")

    rules = checker.addressed_rule

    assert len(rules) == 1
    assert rules[0].rule_uid == "test.com:qc:1.0.0:qwerty.qwerty"


def test_create_rule_id_validation() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    with pytest.raises(
        RuntimeError,
        match=r"Invalid rule uid: .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid="test.com:qc:1.0.0",
        )

    with pytest.raises(
        RuntimeError,
        match=r"Invalid rule uid: .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid="",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\nemanating_entity\n.* String should match pattern .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid=":qc:1.0.0:qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\nstandard\n.* String should match pattern .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid="test.com::1.0.0:qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\ndefinition_setting\n.* String should match pattern .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid="test.com:qc::qwerty.qwerty",
        )

    with pytest.raises(
        ValidationError,
        match=r".*\nrule_full_name\n.* String should match pattern .*",
    ) as exc_info:
        result.register_rule_by_uid(
            checker_bundle_name="TestBundle",
            checker_id="TestChecker",
            rule_uid="test.com:qc:1.0.0:",
        )


def test_build_date() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        description="Example checker bundle",
        version="0.0.1",
    )

    checker_bundle_result = result.get_checker_bundle_result("TestBundle")

    assert checker_bundle_result.build_date == datetime.now().strftime("%Y-%m-%d")
