import os
import pytest
from qc_baselib.models import config, result
from qc_baselib import Result, IssueSeverity, StatusType


DEMO_REPORT_PATH = "tests/data/demo_checker_bundle.xqar"
EXTENDED_DEMO_REPORT_PATH = "tests/data/demo_checker_bundle_extended.xqar"
EXAMPLE_OUTPUT_REPORT_PATH = "tests/data/result_test_output.xqar"
TEST_REPORT_OUTPUT_PATH = "tests/result_test_output.xqar"


@pytest.fixture
def loaded_result() -> Result:
    result = Result()
    result.load_from_file(DEMO_REPORT_PATH)
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
        file_type="odr",
        description="Location for issue",
    )
    result.add_xml_location(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=issue_id,
        xpath="/foo/test/path",
        description="Location for issue",
    )

    result.set_checker_status(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        status=StatusType.COMPLETED,
    )

    result.write_to_file(TEST_REPORT_OUTPUT_PATH)

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


def test_create_issue_load_id() -> None:
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

    assert rule_uid == "test.com:qc:1.0.0:qwerty.qwerty"

    issue_id = result.register_issue(
        checker_bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
        rule_uid=rule_uid,
    )

    assert issue_id == 0
