import os
import pytest
from qc_baselib.models import config, result
from qc_baselib import Result, IssueSeverity


DEMO_REPORT_PATH = "tests/data/demo_checker_bundle.xqar"
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


def test_result_write() -> None:
    result = Result()

    result.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    result.register_checker_to_bundle(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    result.register_issue_to_checker(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=0,
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
    )

    result.add_file_location_to_issue(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=0,
        row=1,
        column=0,
        file_type="odr",
        description="Location for issue",
    )
    result.add_xml_location_to_issue(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=0,
        xpath="/foo/test/path",
        description="Location for issue",
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
    bundles_names = loaded_result.get_checker_bundles_names()

    assert len(bundles_names) == 1

    bundles = loaded_result.get_bundles_results()

    assert len(bundles) == 1
    assert bundles[0].name == "DemoCheckerBundle"


def test_result_checkers_load(loaded_result: Result):
    bundle_checkers = loaded_result.get_checker_bundle_checkers_result(
        bundle_name="DemoCheckerBundle"
    )

    assert len(bundle_checkers) == 1
    assert bundle_checkers[0].checker_id == "exampleChecker"

    example_checker_results = loaded_result.get_checker_result_from_bundle(
        bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
    )

    assert example_checker_results.checker_id == "exampleChecker"


def test_result_issues_load(loaded_result: Result):
    issues = loaded_result.get_issues_from_checker(
        bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
    )

    assert issues[0].description == "This is an information from the demo usecase"
    assert issues[0].issue_id == 0
    assert issues[0].level == IssueSeverity.INFORMATION
