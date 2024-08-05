import os
import argparse
import logging
from datetime import datetime
import json

from qc_baselib import Configuration, Result, IssueSeverity, StatusType

BUNDLE_NAME = "jsonBundle"
BUNDLE_VERSION = "1.0.0"
CHECKER_ID = "jsonChecker"


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def is_valid_json(file_path):
    try:
        with open(file_path, "r") as file:
            json.load(file)
        return True
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return False


def main():
    parser = argparse.ArgumentParser(
        prog="QC JSON Checker",
        description="This is a collection of scripts for checking validity of JSON (.json) files.",
    )

    parser.add_argument("-c", "--config_path")
    args = parser.parse_args()
    logging.info("Initializing checks")

    # Create config object
    config = Configuration()
    config.load_from_file(xml_file_path=args.config_path)

    # Create result object
    result = Result()

    json_file = config.get_config_param("JsonFile")
    result_file = config.get_checker_bundle_param("jsonBundle", "resultFile")

    logging.info(f"JsonFile = {json_file}")
    logging.info(f"resultFile = {result_file}")

    # 1. Register checker bundle
    result.register_checker_bundle(
        name=BUNDLE_NAME,
        build_date=datetime.today().strftime("%Y-%m-%d"),
        description="JSON checker bundle",
        version=BUNDLE_VERSION,
        summary="",
    )
    result.set_result_version(version=BUNDLE_VERSION)

    # 2. Register checker
    result.register_checker(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=CHECKER_ID,
        description="Json validation checker",
        summary="",
    )

    # Register addressed rule
    rule_uid = result.register_rule(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=CHECKER_ID,
        emanating_entity="asam.net",
        standard="json",
        definition_setting="1.0.0",
        rule_full_name="valid_schema",
    )

    # Execute the check logic
    is_valid = is_valid_json(json_file)

    if not is_valid:
        issue_id = result.register_issue(
            checker_bundle_name=BUNDLE_NAME,
            checker_id=CHECKER_ID,
            description="Issue flagging when input file contains no valid json info",
            level=IssueSeverity.ERROR,
            rule_uid=rule_uid,
        )

    logging.info(
        f"Issues found - {result.get_checker_issue_count(checker_bundle_name=BUNDLE_NAME, checker_id=CHECKER_ID)}"
    )
    result.set_checker_status(
        checker_bundle_name=BUNDLE_NAME,
        checker_id=CHECKER_ID,
        status=StatusType.COMPLETED,
    )

    # 4. Write result file
    result.write_to_file(result_file)

    logging.info(f"Report file written to {result_file}")
    logging.info(f"Done")


if __name__ == "__main__":
    main()
