# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Test if XML model encoding and decoding is done properly based on schema
import pytest
from qc_baselib.models import config, result


@pytest.fixture
def demo_config() -> str:
    with open("tests/data/demo_checker_bundle_config.xml", "rb") as config_xml_file:
        return config_xml_file.read()


@pytest.fixture
def demo_report() -> str:
    with open("tests/data/demo_checker_bundle.xqar", "rb") as report_xml_file:
        return report_xml_file.read()


def test_config_model_load(demo_config: str) -> None:
    parsed_config = config.Config.from_xml(demo_config)

    assert len(parsed_config.params) == 1
    assert len(parsed_config.checker_bundles) == 1
    assert len(parsed_config.checker_bundles[0].checkers) == 1


def test_report_model_load(demo_report: str) -> None:
    parsed_report = result.CheckerResults.from_xml(demo_report)

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
