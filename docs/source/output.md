# Output

Each task can either write to the specified directory, or return the
output in memory to the downstream tasks.

If the output directory is `null`, the output will not be dumped / exported,
and passed to the downstream tasks directly.

For example, the below configuration defines `test_dir` as the default
output directory in the `metadata` section.

- `task_a` overrides the output directory as `null` so the output is
  only passed to `task_b` in memory.
- `task_b` writes to the default output directory with its task name.

```
metadata:
  output:
    directory: "test_dir"
task:
  task_a:
    caller: ...
    output:
      directory: null
  task_b:
    caller: ...
    parameters:
      - !data task_a
```

### Format

Currently, the library defines the default behavior of writting and loading
the pickle and JSON formats. For other formats, their loaders and dumpers should
be customised accordingly. The file extension is determined by the format.

Both [JSON](https://docs.python.org/3/library/json.html) and [pickle](https://docs.python.org/3/library/pickle.html) uses the standard library loader and dumper. Pickle will be used by default if not specified.

### Loader and dumper

As mentioned above, if the format is different from the standard library supported
formats, the customised loaders and dumpers should be defined.

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

All the tasks will be written in parquet format and file pattern `<name>.parquet`.

## Existence

Currently, if the output already exists in the output directory, the task
will not be executed and the output is loaded directly.

In the meantime, if you have external dependencies, you can define their
location directly without specifying its caller.

For example, the following configuration expects the file `task_a.pickle`
already exists in the output directory; otherwise, an exception will be
thrown that a caller is expected.

```
task:
  task_a: {}
```