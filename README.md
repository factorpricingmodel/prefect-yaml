# Prefect YAML

<p align="center">
  <a href="https://github.com/factorpricingmodel/prefect-yaml/actions?query=workflow%3ACI">
    <img src="https://img.shields.io/github/workflow/status/factorpricingmodel/prefect-yaml/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://prefect-yaml.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/prefect-yaml.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/factorpricingmodel/prefect-yaml">
    <img src="https://img.shields.io/codecov/c/github/factorpricingmodel/prefect-yaml.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/prefect-yaml/">
    <img src="https://img.shields.io/pypi/v/prefect-yaml.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/prefect-yaml.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/prefect-yaml.svg?style=flat-square" alt="License">
</p>

Package to run prefect with YAML configuration. For further details, please refer
to the [documentation](https://prefect-yaml.readthedocs.io/en/latest/)

## Installation

Install this via pip (or your favourite package manager):

`pip install prefect-yaml`

## Usage

Run the command line `prefect-yaml` with the specified configuration
file.

For example, the following YAML configuration is located in [examples/simple_config.yaml](examples/simple_config.yaml).

```
metadata:
  output-directory: .output

task:
  task_a:
    caller: math:fabs
    parameters:
      - -9.0
    output:
      format: json
  task_b:
    caller: math:sqrt
    parameters:
      - !data task_a
```

Run the following command to generate all the task outputs to the
directory `.output` in the running directory.

```shell
prefect-yaml -c examples/simple_config.yaml
```

The output directory contains all the task outputs in the specified
format. The default format is pickle.

```shell
% tree .output
.output
├── task_a.json
└── task_b.pickle

0 directories, 2 files
```

## Configuration

Each configuration must specify the section of `metadata` and `task`.

### Metadata

Metadata section contains the following parameters.

|     Parameter      |         Description         | Required / Optional |
| :----------------: | :-------------------------: | :-----------------: |
| `output-directory` | Filesystem output directory |      Required       |

### Task

Each task is a key-value pair where the key is the name of the task,
and the value is a dictionary of parameters.

|  Parameter   | Subsection |                                        Description                                        | Required / Optional |
| :----------: | :--------: | :---------------------------------------------------------------------------------------: | :-----------------: |
|   `caller`   |            |          Caller module and function name. In the format of `<module>:<function>`          |      Required       |
| `parameters` |            | Function arguments. Either a list of unnamed arguments or a dictionary of named arguments |     (Optional)      |
|    `name`    |  `output`  |                Name of the output file. Default is same as the task name.                 |     (Optional)      |
|   `format`   |  `output`  |   Output format. Supported stdlib formats are `pickle` and `json`. Default is `pickle`.   |     (Optional)      |
