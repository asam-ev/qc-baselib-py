# Copyright 2024, ASAM e.V.
# This Source Code Form is subject to the terms of the Mozilla
# Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys, os
import logging
import argparse

from qc_baselib import Configuration, Result, IssueSeverity


def is_valid_file(parser: argparse.ArgumentParser, arg: str) -> str:
    """Check if provided argument follows specified extensions

    Args:
        parser (argparse.ArgumentParser): argparse object for handling errors
        arg (str): input argument to check

    Returns:
        str: the argument if valid
    """
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    if not (arg.endswith(".xml") or arg.endswith(".xqar")):
        parser.error("The file must have an .xml or .xqar extension!")
    return arg


def run_text_report(input_filename: str, report_filename: str):
    """Execute text report logic and put the results in report_filename

    Args:
        input_filename (str): Input file from where reading the results to write
        report_filename (str): Txt output file used for representing the result
    """

    result = Result()
    result.load_from_file(input_filename)

    # Open the file in write mode initially to wipe its content
    report_file = open(report_filename, "w")
    report_file.close()

    # Open the file in append mode to add new content
    report_file = open(report_filename, "a")

    report_file.write("=" * 102 + "\n")
    report_file.write("Python Text Report Module - Pooled Results\n")
    report_file.write("=" * 102 + "\n")

    # Checker bundles
    for checker_bundle in result.get_checker_bundle_results():
        report_file.write(f"    CheckerBundle: {checker_bundle.name}\n")
        report_file.write(f"    Build date: {checker_bundle.build_date}\n")
        report_file.write(f"    Build version: {checker_bundle.version}\n")
        report_file.write(f"    Description: {checker_bundle.description}\n")
        report_file.write(f"    Summary: {checker_bundle.summary}\n")
        if len(checker_bundle.params) > 0:
            report_file.write(f"    Parameters:\n")
            for param in checker_bundle.params:
                report_file.write(f"    {param.name} = {param.value}\n")

        # Checkers
        report_file.write("    " + "=" * 20 + "\n")
        report_file.write("    " + "Checkers:\n")
        report_file.write("    " + "=" * 20 + "\n")

        for checker in checker_bundle.checkers:
            report_file.write(f"        Checker:        {checker.checker_id}\n")
            report_file.write(f"        Description:    {checker.description}\n")
            if checker.status is None:
                status_string = ""
            else:
                status_string = checker.status
            report_file.write(f"        Status:    {status_string}\n")
            report_file.write(f"        Summary:        {checker.summary}\n")

            # Issues
            report_file.write("        " + "=" * 20 + "\n")
            report_file.write("        " + "Issues:\n")
            report_file.write("        " + "=" * 20 + "\n")
            for issue in checker.issues:
                report_file.write(f"            Issue:              {issue.issue_id}\n")
                report_file.write(
                    f"            Description:        {issue.description}\n"
                )
                report_file.write(f"            Level:              {issue.level}\n")
            # Addressed rules
            if len(checker.addressed_rule) > 0:

                report_file.write("        " + "=" * 20 + "\n")
                report_file.write("        " + "Addressed rules:\n")
                report_file.write("        " + "=" * 20 + "\n")
                for addressed_rule in checker.addressed_rule:
                    report_file.write(
                        f"            Addressed Rule:     {addressed_rule.rule_uid}\n"
                    )

            # Metadata
            if len(checker.metadata) > 0:
                report_file.write("        " + "=" * 20 + "\n")
                report_file.write("        " + "Metadata:\n")
                report_file.write("        " + "=" * 20 + "\n")
                for metadata in checker.metadata:
                    report_file.write(f"            Metadata:        {metadata.key}\n")
                    report_file.write(f"            Value:        {metadata.value}\n")
                    report_file.write(
                        f"            Description:        {metadata.description}\n"
                    )

    report_file.close()


def main():
    parser = argparse.ArgumentParser(description="Process XML configuration file.")
    parser.add_argument(
        "-f",
        "--file",
        type=lambda x: is_valid_file(parser, x),
        help="Path to the input configuration file. Must be a xml or xqar file",
        required=True,
    )
    args = parser.parse_args()

    input_file = args.file
    input_extension = os.path.splitext(input_file)[1]

    # Default params
    input_filename = "Result.xqar"
    report_filename = "Report.txt"

    if input_extension == ".xqar":
        input_filename = input_file

    # If xml file is provided, the reap input and output file params from it
    if input_extension == ".xml":
        configuration = Configuration()
        configuration.load_from_file(input_file)
        input_filename = configuration.get_config_param("strInputFile")
        report_filename = configuration.get_config_param("strReportFile")

    logging.debug(f"input_filename {input_filename}")
    logging.debug(f"report_filename {report_filename}")

    run_text_report(input_filename, report_filename)


if __name__ == "__main__":
    main()
