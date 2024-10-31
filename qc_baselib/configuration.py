# SPDX-License-Identifier: MPL-2.0
# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Union, List, Dict, Optional
from .models import config, common, IssueSeverity


class Configuration:
    """
    Quality framework `Configuration` schema class.

    This class is responsible for manipulating configuration elements in the
    framework workflow.

    It allow users to read configurations by allowing them
    to load configuration files in memory and get attributes from it.

    ## Example
    ```python
    config = Configuration()

    config.load_from_file(CONFIG_FILE_PATH)

    xodr_file = config.get_config_param("XodrFile")
    ```

    It allows uses to write configuration by allowing them to populate the
    instance of it and write to a file.

    ## Example
    ```python
    config = Configuration()

    config.set_config_param(name="testConfigParamStr", value="testValue")

    config.write_to_file("testConfig.xml")
    ```

    For more information regarding the configuration XSD schema you can check
    [here](https://github.com/asam-ev/qc-framework/blob/main/doc/schema/config_format.xsd).

    """

    def __init__(
        self,
    ):
        self._configuration: Optional[config.Config] = None

    def load_from_file(self, xml_file_path: str, override: bool = False) -> None:
        if self._configuration is not None and not override:
            raise RuntimeError(
                "Configuration already contains data, to re-load it please set the override=True"
            )

        with open(xml_file_path, "rb") as config_xml_file:
            xml_text = config_xml_file.read()
            self._configuration = config.Config.from_xml(xml_text)

    def write_to_file(self, xml_output_file_path: str) -> None:
        if self._configuration is None:
            raise RuntimeError(
                "Configuration dump with None configuration, the configuration needs to be loaded first"
            )
        with open(xml_output_file_path, "wb") as config_xml_file:
            xml_text = self._configuration.to_xml(
                pretty_print=True,
                xml_declaration=True,
                standalone=False,
                encoding="UTF-8",
            )
            config_xml_file.write(xml_text)

    def _get_checker_bundle(
        self, checker_bundle_name: str
    ) -> Optional[config.CheckerBundleType]:
        if len(self._configuration.checker_bundles) == 0:
            return None

        bundle = next(
            (
                bundle
                for bundle in self._configuration.checker_bundles
                if bundle.application == checker_bundle_name
            ),
            None,
        )

        return bundle

    def get_all_checker_bundles(self) -> List[config.CheckerBundleType]:
        return self._configuration.checker_bundles

    def get_all_report_modules(self) -> List[config.ReportModuleType]:
        return self._configuration.reports

    def get_config_param(self, param_name: str) -> Union[str, int, float, None]:
        if len(self._configuration.params) == 0:
            return None

        param = next(
            (param for param in self._configuration.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def get_all_global_config_param(self) -> Dict[str, Union[str, int, float]]:
        params = {}
        for param in self._configuration.params:
            params[param.name] = param.value
        return params

    def get_checker_bundle_param(
        self, checker_bundle_name: str, param_name: str
    ) -> Union[str, int, float, None]:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        if bundle is None or len(bundle.params) == 0:
            return None

        param = next(
            (param for param in bundle.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def get_checker_param(
        self, checker_bundle_name: str, checker_id: str, param_name: str
    ) -> Union[str, int, float, None]:
        bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

        if bundle is None:
            return None

        check = next(
            (check for check in bundle.checkers if check.checker_id == checker_id), None
        )
        if check is None or len(check.params) == 0:
            return None

        param = next(
            (param for param in check.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def get_report_module_param(
        self, checker_bundle_name: str, param_name: str
    ) -> Union[str, int, float, None]:
        if len(self._configuration.reports) == 0:
            return None

        report = next(
            (
                report
                for report in self._configuration.reports
                if report.application == checker_bundle_name
            ),
            None,
        )

        if report is None or len(report.params) == 0:
            return None

        param = next(
            (param for param in report.params if param_name == param.name),
            None,
        )

        if param is None:
            return None

        return param.value

    def register_checker_bundle(self, checker_bundle_name: str) -> None:
        checker_bundle = config.CheckerBundleType.model_construct(
            **{"application": checker_bundle_name}
        )

        if self._configuration is None:
            self._configuration = config.Config.model_construct(
                **{"checker_bundles": [checker_bundle]}
            )

        else:
            self._configuration.checker_bundles.append(checker_bundle)

    def register_checker(
        self,
        checker_bundle_name: str,
        checker_id: str,
        min_level: IssueSeverity,
        max_level: IssueSeverity,
    ) -> None:
        """
        Checker with checker_id will be registered to the checker bundle
        identified by the checker_bundle_name.
        """
        check = config.CheckerType(
            checker_id=checker_id, min_level=min_level, max_level=max_level
        )

        if self._configuration is None:
            raise RuntimeError(
                "Adding check to empty configuration. Initialize the config registering first a checker bundle."
            )
        else:
            bundle = self._get_checker_bundle(checker_bundle_name=checker_bundle_name)

            if bundle is None:
                raise RuntimeError(
                    f"Adding check to non-existent '{checker_bundle_name}' checker bundle. Register first the checker bundle."
                )
            bundle.checkers.append(check)

    def set_config_param(self, name: str, value: Union[int, float, str]) -> None:
        param = common.ParamType(name=name, value=value)

        if self._configuration is None:
            self._configuration = config.Config(params=[param])
        else:
            self._configuration.params.append(param)

    def set_checker_bundle_param(
        self, checker_bundle_name: str, name: str, value: Union[int, float, str]
    ) -> None:
        param = common.ParamType(name=name, value=value)

        if self._configuration is None:
            raise RuntimeError(
                "Adding param to empty configuration. Initialize the config registering first an initial element."
            )
        else:
            bundle = next(
                (
                    bundle
                    for bundle in self._configuration.checker_bundles
                    if bundle.application == checker_bundle_name
                ),
                None,
            )

            if bundle is None:
                raise RuntimeError(
                    f"Adding param to non-existent '{checker_bundle_name}' checker bundle. Register first the checker bundle."
                )
            bundle.params.append(param)

    def set_checker_param(
        self,
        checker_bundle_name: str,
        checker_id: str,
        name: str,
        value: Union[str, int, float],
    ) -> None:
        param = common.ParamType(name=name, value=value)

        if self._configuration is None:
            raise RuntimeError(
                "Adding param to empty configuration. Initialize the config registering first an initial element."
            )
        else:
            bundle = next(
                (
                    bundle
                    for bundle in self._configuration.checker_bundles
                    if bundle.application == checker_bundle_name
                ),
                None,
            )

            if bundle is None:
                raise RuntimeError(
                    f"Adding param to non-existent '{checker_bundle_name}' checker bundle. Register first the checker bundle."
                )

            check = next(
                (check for check in bundle.checkers if check.checker_id == checker_id),
                None,
            )
            if check is None:
                raise RuntimeError(
                    f"Adding param to non-existent '{checker_bundle_name}' checker bundle. Register first the checker bundle."
                )
            check.params.append(param)
