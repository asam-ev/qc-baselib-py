# Python text report module

The module reads an input .xqar file and create e report .txt file with a textual representation of the report content

## Usage

```
./report_format_text.sh input.xqar
```

Output will be a `Report.txt` file

It is also possible to read an input configuration file

```
./report_format_text.sh checker_config.xml
```

In this case, the xml file will be processed and the input xqar file will be read from configuration `Param` node with name `strInputFile`

e.g.

```
  <ReportModule application="TextReport">
    <Param name="strInputFile" value="Result.xqar"/>
    <Param name="strReportFile" value="Report.txt"/>
  </ReportModule>
```

in this case the `Result.xqar` will be processed


## Example output

```
======================================================================================================
Python Text Report Module - Pooled Results
======================================================================================================

    CheckerBundle: DemoCheckerBundle
    Build date: 
    Build version: 
    Description: 
    Summary: Found 1 issue
    ====================
    Checkers:
    ====================

        Checker:        exampleChecker
        Description:    This is a description
        Status:    
        Summary:        
        ====================
        Issues:
        ====================
        ====================
        Addressed rules:
        ====================
            Addressed Rule:     asam.net:xosc:1.0.0:xml.valid_schema

```