import pytest
from qc_baselib.models import config, report
from qc_baselib.configuration import Configuration


@pytest.fixture
def demo_config() -> str:
    return "tests/data/DemoCheckerBundle_config.xml"


@pytest.fixture
def loaded_config(demo_config: str) -> Configuration:
    config = Configuration()
    config.load_from_file(demo_config)
    return config


def test_get_config_param(loaded_config: Configuration) -> None:
    assert loaded_config.get_config_param("XodrFile")


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
    config.register_checker_to_bundle(
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
    config.register_checker_to_bundle(
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
