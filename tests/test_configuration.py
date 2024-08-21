# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import pytest
from qc_baselib.models import config, result
from qc_baselib import Configuration

TEST_DATA_BASE_PATH = "tests/data"
DEMO_CONFIG_PATH = "tests/data/demo_checker_bundle_config.xml"
EXAMPLE_OUTPUT_CONFIG_PATH = "tests/data/config_test_output.xml"
TEST_CONFIG_OUTPUT_PATH = "tests/config_test_output.xml"


@pytest.fixture
def loaded_config() -> Configuration:
    config = Configuration()
    config.load_from_file(DEMO_CONFIG_PATH)
    return config


def test_get_config_param(loaded_config: Configuration) -> None:
    assert (
        loaded_config.get_config_param("XodrFile")
        == "../stimuli/xodr_examples/three_connected_roads_with_steps.xodr"
    )


def test_get_checker_bundle_param(loaded_config: Configuration) -> None:
    assert (
        loaded_config.get_checker_bundle_param("DemoCheckerBundle", "strResultFile")
        == "DemoCheckerBundle.xqar"
    )


def test_get_check_param(loaded_config: Configuration) -> None:
    assert (
        loaded_config.get_checker_param(
            "DemoCheckerBundle", "exampleChecker", "testCheckerParam"
        )
        == "Foo"
    )


# TODO: Add missing get report module config param tests


def test_set_config_param() -> None:
    config = Configuration()

    config.set_config_param("testConfigParamStr", "testValue")
    config.set_config_param("testConfigParamInt", 1)
    config.set_config_param("testConfigParamFloat", 2.0)

    assert config.get_config_param("testConfigParamStr") == "testValue"
    assert config.get_config_param("testConfigParamInt") == 1
    assert config.get_config_param("testConfigParamFloat") == 2.0
    assert config.get_config_param("None") == None


def test_register_checker_bundle() -> None:
    config = Configuration()

    config.register_checker_bundle("TestCheckerBundle")


def test_register_checker_to_bundle() -> None:
    config = Configuration()

    config.register_checker_bundle("TestCheckerBundle")
    config.register_checker(
        "TestCheckerBundle", "TestChecker", min_level=1, max_level=3
    )


def test_set_checker_bundle_param() -> None:
    config = Configuration()

    config.register_checker_bundle("TestCheckerBundle")

    config.set_checker_bundle_param("TestCheckerBundle", "testCbParamStr", "testValue")
    config.set_checker_bundle_param("TestCheckerBundle", "testCbParamInt", 1)
    config.set_checker_bundle_param("TestCheckerBundle", "testCbParamFloat", 2.0)

    assert (
        config.get_checker_bundle_param("TestCheckerBundle", "testCbParamStr")
        == "testValue"
    )
    assert config.get_checker_bundle_param("TestCheckerBundle", "testCbParamInt") == 1
    assert (
        config.get_checker_bundle_param("TestCheckerBundle", "testCbParamFloat") == 2.0
    )


def test_set_checker_param() -> None:
    config = Configuration()

    config.register_checker_bundle("TestCheckerBundle")
    config.register_checker(
        "TestCheckerBundle", "TestChecker", min_level=1, max_level=3
    )

    config.set_checker_param(
        "TestCheckerBundle", "TestChecker", "testCbParamStr", "testValue"
    )
    config.set_checker_param("TestCheckerBundle", "TestChecker", "testCbParamInt", 1)
    config.set_checker_param(
        "TestCheckerBundle", "TestChecker", "testCbParamFloat", 2.0
    )

    assert (
        config.get_checker_param("TestCheckerBundle", "TestChecker", "testCbParamStr")
        == "testValue"
    )
    assert (
        config.get_checker_param("TestCheckerBundle", "TestChecker", "testCbParamInt")
        == 1
    )
    assert (
        config.get_checker_param("TestCheckerBundle", "TestChecker", "testCbParamFloat")
        == 2.0
    )


def test_config_write() -> None:
    config = Configuration()

    config.set_config_param(name="testConfigParamStr", value="testValue")
    config.set_config_param(name="testConfigParamInt", value=1)
    config.set_config_param(name="testConfigParamFloat", value=2.0)

    config.register_checker_bundle(checker_bundle_name="TestCheckerBundle")
    config.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        min_level=1,
        max_level=3,
    )

    # Creating using named arguments
    config.set_checker_param(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="testCbParamStr",
        value="testValue",
    )
    config.set_checker_param(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        name="testCbParamInt",
        value=1,
    )
    # Creating using the positional
    config.set_checker_param(
        "TestCheckerBundle",
        "TestChecker",
        "testCbParamFloat",
        2.0,
    )

    config.write_to_file(TEST_CONFIG_OUTPUT_PATH)

    example_xml_text = ""
    output_xml_text = ""
    with open(EXAMPLE_OUTPUT_CONFIG_PATH, "r") as config_xml_file:
        example_xml_text = config_xml_file.read()
    with open(TEST_CONFIG_OUTPUT_PATH, "r") as config_xml_file:
        output_xml_text = config_xml_file.read()

    assert output_xml_text == example_xml_text

    os.remove(TEST_CONFIG_OUTPUT_PATH)


def test_config_file_parse_order_independence() -> None:
    config_unordered = Configuration()
    config_unordered.load_from_file(
        os.path.join(TEST_DATA_BASE_PATH, "unordered_config.xml")
    )

    config_ordered = Configuration()
    config_ordered.load_from_file(
        os.path.join(TEST_DATA_BASE_PATH, "ordered_config.xml")
    )

    assert len(config_ordered._configuration.reports) == len(
        config_unordered._configuration.reports
    )

    assert len(config_ordered._configuration.checker_bundles) == len(
        config_unordered._configuration.checker_bundles
    )

    assert len(config_ordered._configuration.params) == len(
        config_unordered._configuration.params
    )
