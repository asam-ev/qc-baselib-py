from typing import Union, Dict
from models import config, common


class Configuration:
    def __init__(
        self,
    ):
        self._configuration: Union[None, config.Config] = None

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
                pretty_print=True, xml_declaration=True, standalone=False
            )
            config_xml_file.write(xml_text)

    def get_config_param(self, param_name: str) -> str:
        if len(self._configuration.params) == 0:
            return ""

        param = next(
            (param for param in self._configuration.params if param_name == param.name),
            None,
        )

        if param is None:
            return ""

        return param.value

    def get_checker_bundle_param(self, application: str, param_name: str) -> str:
        if len(self._configuration.checker_bundles) == 0:
            return ""

        bundle = next(
            bundle
            for bundle in self._configuration.checker_bundles
            if bundle.application == application
        )

        if bundle is None or len(bundle.params) == 0:
            return ""

        param = next(
            (param for param in bundle.params if param_name == param.name),
            None,
        )

        if param is None:
            return ""

        return param.value

    def get_report_module_param(self, application: str, param_name: str) -> str:
        if len(self._configuration.reports) == 0:
            return ""

        report = next(
            report
            for report in self._configuration.reports
            if report.application == application
        )

        if report is None or len(report.params) == 0:
            return ""

        param = next(
            (param for param in report.params if param_name == param.name),
            None,
        )

        if param is None:
            return ""

        return param.value

    def register_checker_bundle(self, application: str) -> None:
        checker_bundle = config.CheckerBundleType.model_construct(
            {"application": application}
        )

        if self._configuration is None:
            self._configuration = config.Config(checker_bundles=[checker_bundle])
        else:
            self._configuration.checker_bundles.append(checker_bundle)

    def register_check_to_bundle(
        self, application: str, check_id: str, min_level: str, max_level: str
    ) -> None:
        check = config.CheckerType(
            check_id=check_id, min_level=min_level, max_level=max_level
        )

        if self._configuration is None:
            raise RuntimeError(
                "Adding check to empty configuration. Initialize the config registering first a checker bundle."
            )
        else:
            bundle = next(
                bundle
                for bundle in self._configuration.checker_bundles
                if bundle.application == application
            )

            if bundle is None or len(bundle.params) == 0:
                raise RuntimeError(
                    f"Adding check to non-existent '{application}' checker bundle. Register first the checker bundle."
                )
            bundle.checks.append(check)

    def set_checker_bundle_param(
        self, application: str, name: str, value: Union[int, float, str]
    ) -> None:
        param = common.ParamType(name=name, value=value)

        if self._configuration is None:
            raise RuntimeError(
                "Adding param to empty configuration. Initialize the config registering first an initial element."
            )
        else:
            bundle = next(
                bundle
                for bundle in self._configuration.checker_bundles
                if bundle.application == application
            )

            if bundle is None or len(bundle.params) == 0:
                raise RuntimeError(
                    f"Adding param to non-existent '{application}' checker bundle. Register first the checker bundle."
                )
            bundle.params.append(param)

    def set_check_param(
        self, application: str, check_id: str, name: str, value: Union[str, int, float]
    ) -> None:
        param = common.ParamType(name=name, value=value)

        if self._configuration is None:
            raise RuntimeError(
                "Adding param to empty configuration. Initialize the config registering first an initial element."
            )
        else:
            bundle = next(
                bundle
                for bundle in self._configuration.checker_bundles
                if bundle.application == application
            )

            if bundle is None or len(bundle.params) == 0:
                raise RuntimeError(
                    f"Adding param to non-existent '{application}' checker bundle. Register first the checker bundle."
                )

            check = next(
                check for check in bundle.checks if check.checker_id == check_id
            )
            check.params.append(param)

    # def set_config_param(self, param_name: str) -> None:
    #     return

    # def set_report_module_param(self, application: str, param_name: str) -> None:
    #     return
