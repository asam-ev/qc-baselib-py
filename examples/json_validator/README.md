# qc-json

This project implements a test JSON checker for the ASAM Quality Checker project.


## Installation

To install the project, run:

```
pip install -r requirements.txt
```

This will install the needed dependencies to your local Python.

## Usage

The checker can be used as a Python script:

```
python json_validator.py --help

usage: QC JSON Checker [-h] (-c CONFIG_PATH)

This is a collection of scripts for checking validity of OpenDrive (.xodr) files.

options:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config_path CONFIG_PATH

```

### Example

- No issues found

```
$ python json_validator.py -c config/valid.xml
2024-08-05 10:38:07,978 - Initializing checks
2024-08-05 10:38:07,979 - JsonFile = data/valid.json
2024-08-05 10:38:07,979 - resultFile = json_bundle_report.xqar
2024-08-05 10:38:07,979 - Issues found - 0
2024-08-05 10:38:07,979 - Report file written to json_bundle_report.xqar
2024-08-05 10:38:07,979 - Done
```

- Issues found on file

```
$ python json_validator.py -c config/invalid.xml
2024-08-05 10:38:11,946 - Initializing checks
2024-08-05 10:38:11,946 - JsonFile = data/invalid.json
2024-08-05 10:38:11,946 - resultFile = json_bundle_report.xqar
2024-08-05 10:38:11,947 - Issues found - 1
2024-08-05 10:38:11,947 - Report file written to json_bundle_report.xqar
2024-08-05 10:38:11,947 - Done
```
