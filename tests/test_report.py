import os
import pytest
from qc_baselib.models import config, report
from qc_baselib import Report, IssueSeverity


DEMO_REPORT_PATH = "tests/data/demo_checker_bundle.xqar"
EXAMPLE_OUTPUT_REPORT_PATH = "tests/data/report_test_output.xqar"
TEST_REPORT_OUTPUT_PATH = "tests/report_test_output.xqar"


@pytest.fixture
def loaded_report() -> Report:
    report = Report()
    report.load_from_file(DEMO_REPORT_PATH)
    return report


def test_load_report_from_file() -> None:
    report = Report()
    report.load_from_file(DEMO_REPORT_PATH)
    assert len(report._report_results.to_xml()) > 0


# TODO: Finalize tests for Report


def test_report_write() -> None:
    report = Report()

    report.register_checker_bundle(
        name="TestBundle",
        build_date="2024-05-31",
        description="Example checker bundle",
        version="0.0.1",
        summary="Tested example checkers",
    )

    report.register_checker_to_bundle(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        description="Test checker",
        summary="Executed evaluation",
    )

    report.register_issue_to_checker(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=0,
        description="Issue found at odr",
        level=IssueSeverity.INFORMATION,
    )

    report.add_file_location_to_issue(
        bundle_name="TestBundle",
        checker_id="TestChecker",
        issue_id=0,
        row=1,
        column=0,
        file_type="odr",
        description="Location for issue",
    )
    # xml and road location are also supported

    report.write_to_file(TEST_REPORT_OUTPUT_PATH)

    example_xml_text = ""
    output_xml_text = ""
    with open(EXAMPLE_OUTPUT_REPORT_PATH, "r") as report_xml_file:
        example_xml_text = report_xml_file.read()
    with open(TEST_REPORT_OUTPUT_PATH, "r") as report_xml_file:
        output_xml_text = report_xml_file.read()

    assert output_xml_text == example_xml_text

    os.remove(TEST_REPORT_OUTPUT_PATH)
