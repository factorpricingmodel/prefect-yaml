# Prefect YAML

<p align="center">
  <a href="https://github.com/factorpricingmodel/prefect-yaml/actions?query=workflow%3ACI">
    <img src="https://github.com/factorpricingmodel/prefect-yaml/actions/workflows/ci.yml/badge.svg" alt="CI Status" >
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
  output:
    directory: .output

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
    output:
      directory: null
  task_c:
    caller: math:fsum
    parameters:
      - [!data task_b, 1]
```

Run the following command to generate all the task outputs to the
directory `.output` in the running directory.

```shell
prefect-yaml -c examples/simple_config.yaml
```

The output directory contains all the task outputs in the specified
format.

```shell
% tree .output
.output
├── task_a.json
└── task_c.pickle

0 directories, 2 files
```

The expected behavior is to

1. run `task_a` to dump the value `fabs(-9.0)` to the output directory in JSON format,
2. run `task_b` to get the value `sqrt(9.0)` (from the output of `task_a`)
3. run `task_c` to dump the value `fsum([3.0, 1.0])` to the output directory in pickle format.

As the output directory in `task_b` is overridden as `null`, the output of `task_b` is passed to `task_c` in memory. Also, the output format in `task_c`
is not specified so it is dumped in default format (pickle).

For further details, please see the section [configuration](https://prefect-yaml.readthedocs.io/en/latest/configuration.html) in the documentation.

## Configuration

The output section defines how the task writes and loads the task return. The section in `metadata` applies for all tasks globally while that in each `task`
overrides the global parameters.

For further details, please see the [documentation](https://prefect-yaml.readthedocs.io/en/latest/configuration.html#output) for parameter definitions
in each section.

## Output

The default output format is either pickle (default) or JSON, while users
can define their own output format.

For example, if you would like to use `pandas` to load and dump the parquet file
in pyarrow engine by default, you can define the configuration like below.

```
metadata:
  format: parquet
  dump-caller: object.to_parquet
  dump-parameters:
    engine: pyarrow
  load-caller: pandas:read_parquet
  load-parameters:
    engine: pyarrow
```

All the output parameters, like directory, dumper and loaders, can be overridden
in the task level. You can also specify which tasks to export to the output
directory, while the others to only be passed down to downstream in memory.

For further details, please see the [output](https://prefect-yaml.readthedocs.io/en/latest/output.html) section in documentation.

## Roadmap

Currently the project is still under development. The basic features are
mostly available while the following features are coming soon

- Multi cloud storage support
- Subtasks supported in each task
-

## Contributing

All levels of contributions are welcomed. Please refer to the [contributing](https://prefect-yaml.readthedocs.io/en/latest/contributing.html)
section for development and release guidelines.
