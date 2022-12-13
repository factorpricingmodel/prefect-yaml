# Usage

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
