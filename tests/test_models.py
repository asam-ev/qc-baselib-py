# Test if XML model encoding and decoding is done properly based on schema
import pytest
from qc_baselib.models import config, report


@pytest.fixture
def demo_config() -> str:
    # dump to text file on test/data and load fpr the test
    return """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!--
Copyright 2023 CARIAD SE.

This Source Code Form is subject to the terms of the Mozilla
Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->
<Config>

  <Param name="XodrFile" value="../stimuli/xodr_examples/three_connected_roads_with_steps.xodr"/>

  <CheckerBundle application="DemoCheckerBundle">
    <Param name="strResultFile" value="DemoCheckerBundle.xqar"/>
    <Checker checkerId="exampleChecker" maxLevel="1" minLevel="3"/>
  </CheckerBundle>

</Config>
"""


@pytest.fixture
def demo_report() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<CheckerResults version="1.0.0">

  <CheckerBundle build_date="" description="" name="DemoCheckerBundle" summary="Found 1 issue" version="">
    <Checker checkerId="exampleChecker" description="This is a description" summary="">
      <Issue description="This is an information from the demo usecase" issueId="0" level="3"/>
    </Checker>
  </CheckerBundle>

</CheckerResults>
"""


def test_config_model_load(demo_config: str) -> None:
    parsed_config = config.Config.from_xml(demo_config)

    assert len(parsed_config.params) == 1
    assert len(parsed_config.checker_bundles) == 1
    assert len(parsed_config.checker_bundles[0].checks) == 1


def test_report_model_load(demo_report: str) -> None:
    parsed_report = report.CheckerResults.from_xml(demo_report)

    assert parsed_report.version == "1.0.0"
    assert len(parsed_report.checker_bundles) == 1
    assert len(parsed_report.checker_bundles[0].checkers) == 1
    assert parsed_report.checker_bundles[0].checkers[0].checker_id == "exampleChecker"
    assert (
        parsed_report.checker_bundles[0].checkers[0].description
        == "This is a description"
    )
    assert len(parsed_report.checker_bundles[0].checkers[0].issues) == 1
    assert (
        parsed_report.checker_bundles[0].checkers[0].issues[0].description
        == "This is an information from the demo usecase"
    )
