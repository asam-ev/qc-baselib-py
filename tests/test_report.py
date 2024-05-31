import os
import pytest
from qc_baselib.models import config, report
from qc_baselib.report import Report


DEMO_REPORT_PATH = "tests/data/DemoCheckerBundle.xqar"
EXAMPLE_OUTPUT_REPORT_PATH = "tests/data/ReportTestOutput.xml"
TEST_REPORT_OUTPUT_PATH = "tests/ReportTestOutput.xqar"


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
