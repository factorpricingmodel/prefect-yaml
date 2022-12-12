# Configuration

Each configuration must specify the section of `metadata` and `task`.

## Metadata

Metadata section contains the following parameters.

|     Parameter      |         Description         | Required / Optional |
| :----------------: | :-------------------------: | :-----------------: |
| `output-directory` | Filesystem output directory |      Required       |

## Task

Each task is a key-value pair where the key is the name of the task,
and the value is a dictionary of parameters.

|  Parameter   | Subsection |                                        Description                                        | Required / Optional |
| :----------: | :--------: | :---------------------------------------------------------------------------------------: | :-----------------: |
|   `caller`   |            |          Caller module and function name. In the format of `<module>:<function>`          |      Required       |
| `parameters` |            | Function arguments. Either a list of unnamed arguments or a dictionary of named arguments |     (Optional)      |
|   `format`   |  `output`  |   Output format. Supported stdlib formats are `pickle` and `json`. Default is `pickle`.   |     (Optional)      |
|    `name`    |  `output`  |                Name of the output file. Default is same as the task name.                 |     (Optional)      |
