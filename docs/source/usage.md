# Usage

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