[![Tests](https://github.com/asam-ev/qc-baselib-py/actions/workflows/tests.yml/badge.svg)](https://github.com/asam-ev/qc-baselib-py/actions?workflow=Tests)

# asam-qc-baselib

The ASAM Quality Checker Python Base Library (asam-qc-baselib) implements a Python interface for
interacting with the configuration files and the results files from the
ASAM Quality Checker Framework. With it, users can create their own
Checker Bundles or Report Modules in Python.

The library features the main interfaces needed to implement a module:

- Configuration: for reading and writing QC Framework [configuration files](https://github.com/asam-ev/qc-framework/blob/main/doc/manual/file_formats.md#configuration-file-xml).
- Results: for reading and writing QC Framework [result files](https://github.com/asam-ev/qc-framework/blob/main/doc/manual/file_formats.md#result-file-xqar).

## Installation

### Installation using pip

**From PyPi**

```bash
pip install asam-qc-baselib
```

**From GitHub repository**

```bash
pip install asam-qc-baselib@git+https://github.com/asam-ev/qc-baselib-py@main
```

To install from different sources, you can replace `@main` with
your desired target. For example, `develop` branch as `@develop`.

**From a local repository**

```bash
pip install /home/user/qc-baselib-py
```

### Installation from source for local development.

Using [Poetry](https://python-poetry.org/):

```bash
poetry install --with dev
```

## Examples

### Creating checker bundle configuration and adding checkers

- Create a file `main.py` with:

```python
from qc_baselib import Configuration, IssueSeverity

def main():
    config = Configuration()

    config.set_config_param(name="testConfigParamStr", value="testValue")
    config.set_config_param(name="testConfigParamInt", value=1)
    config.set_config_param(name="testConfigParamFloat", value=2.0)

    config.register_checker_bundle(checker_bundle_name="TestCheckerBundle")
    config.register_checker(
        checker_bundle_name="TestCheckerBundle",
        checker_id="TestChecker",
        min_level=IssueSeverity.ERROR,
        max_level=IssueSeverity.INFORMATION,
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

    config.write_to_file("testConfig.xml")

if __name__ == "__main__":
    main()

```

- Execute the script

```bash
python main.py
```

The script will produce a XML file `testConfig.xml` with the following
content:

```xml
<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<Config>
  <Param name="testConfigParamStr" value="testValue"/>
  <Param name="testConfigParamInt" value="1"/>
  <Param name="testConfigParamFloat" value="2.0"/>
  <CheckerBundle checker_bundle_name="TestCheckerBundle">
    <Checker checkerId="TestChecker" maxLevel="3" minLevel="1">
      <Param name="testCbParamStr" value="testValue"/>
      <Param name="testCbParamInt" value="1"/>
      <Param name="testCbParamFloat" value="2.0"/>
    </Checker>
  </CheckerBundle>
</Config>
```

For more information regarding the configuration XSD schema you can check [here](https://github.com/asam-ev/qc-framework/blob/main/doc/schema/config_format.xsd)

### Reading checker bundle config from file

- Create a file `main.py` with:

```python
from qc_baselib import Configuration

CONFIG_FILE_PATH = "tests/data/demo_checker_bundle_config.xml"

def main():
    loaded_config = Configuration()

    loaded_config.load_from_file(CONFIG_FILE_PATH)

    xodr_file = loaded_config.get_config_param("XodrFile")
    demo_bundle_str_result_file = loaded_config.get_checker_bundle_param(
        "DemoCheckerBundle", "strResultFile"
    )
    example_checker_param = loaded_config.get_checker_param(
        "DemoCheckerBundle", "exampleChecker", "testCheckerParam"
    )

    print(f"XodrFile = {xodr_file}")
    print(f"DemoCheckerBundle.strResultFile = {demo_bundle_str_result_file}")
    print(
        f"DemoCheckerBundle.exampleChecker.testCheckerParam = {example_checker_param}"
    )


if __name__ == "__main__":
    main()

```

- Execute the script

```bash
python main.py
```

The script will load the configuration into the `loaded_config` object and
will output:

```
XodrFile = ../stimuli/xodr_examples/three_connected_roads_with_steps.xodr
DemoCheckerBundle.strResultFile = DemoCheckerBundle.xqar
DemoCheckerBundle.exampleChecker.testCheckerParam = Foo
```

### Writing a result for checker results

- Create a file `main.py` with:

```python
from qc_baselib import Result, IssueSeverity

def main():
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

    result.write_to_file("testResults.xqar")

if __name__ == "__main__":
    main()

```

- Execute the script

```bash
python main.py
```

The script will produce a XML file `testResults.xqar` with the following
content:

```xml
<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<CheckerResults version="0.0.1">
  <CheckerBundle build_date="2024-05-31" description="Example checker bundle" name="TestBundle" version="0.0.1" summary="Tested example checkers">
    <Checker checkerId="TestChecker" description="Test checker" summary="Executed evaluation">
      <Issue issueId="0" description="Issue found at odr" level="3">
        <Location description="Location for issue">
          <FileLocation column="0" row="1" fileType="odr"/>
        </Location>
      </Issue>
    </Checker>
  </CheckerBundle>
</CheckerResults>

```

For more information regarding the result XSD schema you can check [here](https://github.com/asam-ev/qc-framework/blob/main/doc/schema/xqar_result_format.xsd)

### Reading a result from checker bundle execution

- Create a file `main.py` with:

```python
from qc_baselib import Result

def main():
    result = Result()
    result.load_from_file("tests/data/demo_checker_bundle.xqar")

    bundles_names = result.get_checker_bundle_names()

    print(f"Bundle names: {bundles_names}")

    checker_results = result.get_checker_results(
        checker_bundle_name="DemoCheckerBundle"
    )

    print(f"Checker id: {checker_results[0].checker_id}")

    issues = result.get_issues(
        checker_bundle_name="DemoCheckerBundle", checker_id="exampleChecker"
    )

    print(f"Issue description: {issues[0].description}")
    print(f"Issue id: {issues[0].issue_id}")
    print(f"Issue level: {issues[0].level}")

if __name__ == "__main__":
    main()

```

- Execute the script

```bash
python main.py
```

The script will output something similar to:

```
Bundle names: ['DemoCheckerBundle']
Checker id: exampleChecker
Issue description: This is an information from the demo use case
Issue id: 0
Issue level: 3
```

For more use case examples refer to the library [tests](tests/).

## Tests

- Install module on development mode

```bash
poetry install --with dev
```

- Execute tests

```bash
poetry run pytest
```

The tests should output something similar to:

```bash
=============== test session starts ===============
platform linux -- Python 3.11.9, pytest-8.2.1, pluggy-1.5.0
rootdir: /home/tripel/asam/qc-baselib-py
configfile: pyproject.toml
collected 13 items

tests/test_configuration.py .........                                                                                                                                               [ 69%]
tests/test_models.py ..                                                                                                                                                             [ 84%]
tests/test_result.py ..                                                                                                                                                             [100%]

=============== 13 passed in 0.20s ===============
```

For verbose mode run:

```bash
poetry run pytest -vv
```

```bash
=============== test session starts ===============
platform linux -- Python 3.11.9, pytest-8.2.1, pluggy-1.5.0 -- /home/tripel/.cache/pypoetry/virtualenvs/qc-baselib-6AF2_5rC-py3.11/bin/python
cachedir: .pytest_cache
rootdir: /home/tripel/asam/qc-baselib-py
configfile: pyproject.toml
collected 13 items

tests/test_configuration.py::test_get_config_param PASSED                                                                                                                           [  7%]
tests/test_configuration.py::test_get_checker_bundle_param PASSED                                                                                                                   [ 15%]
tests/test_configuration.py::test_get_check_param PASSED                                                                                                                            [ 23%]
tests/test_configuration.py::test_set_config_param PASSED                                                                                                                           [ 30%]
tests/test_configuration.py::test_register_checker_bundle PASSED                                                                                                                    [ 38%]
tests/test_configuration.py::test_register_checker_to_bundle PASSED                                                                                                                 [ 46%]
tests/test_configuration.py::test_set_checker_bundle_param PASSED                                                                                                                   [ 53%]
tests/test_configuration.py::test_set_checker_param PASSED                                                                                                                          [ 61%]
tests/test_configuration.py::test_config_write PASSED                                                                                                                               [ 69%]
tests/test_models.py::test_config_model_load PASSED                                                                                                                                 [ 76%]
tests/test_models.py::test_result_model_load PASSED                                                                                                                                 [ 84%]
tests/test_result.py::test_load_result_from_file PASSED                                                                                                                             [ 92%]
tests/test_result.py::test_result_write PASSED                                                                                                                                      [100%]

=============== 13 passed in 0.21s ===============
```

You can check more options for pytest at its [own documentation](https://docs.pytest.org/).
