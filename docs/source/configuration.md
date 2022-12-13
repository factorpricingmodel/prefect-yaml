# Configuration

Each configuration must specify the section of `metadata` and `task`. Metadata and each task can define the `output` section.

## Metadata

Metadata section contains the following parameters / sections.

| Parameter / Section |                            Description                             |
| :-----------------: | :----------------------------------------------------------------: |
|      `output`       | Output section. For further details, please see the below section. |

## Task

Each task is a key-value pair where the key is the name of the task,
and the value is a dictionary of parameters.

|  Parameter   | Subsection |                                        Description                                        | Required / Optional |
| :----------: | :--------: | :---------------------------------------------------------------------------------------: | :-----------------: |
|   `caller`   |            |          Caller module and function name. In the format of `<module>:<function>`          |      Required       |
| `parameters` |            | Function arguments. Either a list of unnamed arguments or a dictionary of named arguments |     (Optional)      |

## Output

The output section defines how the task writes and loads the task return. The section in `metadata` applies for all tasks globally while that in each `task`
overrides the global parameters.

|     Parameter     |                                                                                                    Description                                                                                                     |
| :---------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|      `name`       |                                                                             Name of the output file. Default is same as the task name.                                                                             |
|     `format`      |                                                               Output format. Supported stdlib formats are `pickle` and `json`. Default is `pickle`.                                                                |
|   `load-caller`   |                                   Caller to load the output formatted in `<module>:<function>`. The function / method should accept the task return value as the first argument.                                   |
| `load-parameters` |                                                            Dictionary of named parameters of the load function / method, other than the first argument.                                                            |
|   `dump-caller`   | Caller to dump the output formatted either in `<module>:<function>` or `object.<method>`. The function / method should accept the task return value and output path as the first and second argument respectively. |
| `dump-parameters` |                                                         Dictionary of named parameters of the dump function / method, other than the first two arguments.                                                          |
