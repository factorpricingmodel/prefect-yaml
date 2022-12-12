from os.path import join as fsjoin
from importlib import import_module
import re

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from .config import Data, load_configuration, get_data_queue


def _parse_dependencies(data_futures, parameters):
    if isinstance(parameters, dict):
        dependencies = {}
        for key, value in parameters.items():
            if isinstance(value, Data):
                if value.name not in data_futures:
                    raise ValueError(
                        f"Value {value.name} should be in the data futures. "
                        f"Current future list = {list(data_futures.keys())}"
                    )
                dependencies[key] = data_futures[value.name]
            else:
                dependencies[key] = value
    elif isinstance(parameters, list):
        dependencies = []
        for value in parameters:
            if isinstance(value, Data):
                if value.name not in data_futures:
                    raise ValueError(
                        f"Value {value.name} should be in the data futures. "
                        f"Current future list = {list(data_futures.keys())}"
                    )
                dependencies.append(data_futures[value.name])
            else:
                dependencies.append(value)
    else:
        raise TypeError("Parameters type {parameters} is not supported")

    return dependencies


def _output(metadata, name, value, output):
    output_directory = metadata["output-directory"]
    output_name = output.get("name", name)
    output_format = output.get("format", "pickle")
    output_path = fsjoin(output_directory, f"{output_name}.{output_format}")
    if output_format == "pickle":
        from pickle import dump as pickle_dump

        with open(output_path, mode="wb") as f:
            pickle_dump(value, f)
    elif output_format == "json":
        from json import dump as json_dump

        with open(output_path, mode="w") as f:
            json_dump(value, f)
    else:
        raise ValueError(f"Output format {output_format} is not supported")

    return value


@task
def _task(name, description, metadata, **kwargs):
    def is_args(kwargs):
        return all([re.match("^_\d+$", k) is not None for k in kwargs.keys()])

    caller = description["caller"]
    module_name, function_name = caller.split(":")
    module = import_module(module_name)
    func = getattr(module, function_name)
    print(list(kwargs.values()))

    if is_args(kwargs):
        value = func(*[v for v in kwargs.values()])
    else:
        value = func(**kwargs)

    return _output(
        metadata=metadata,
        name=name,
        value=value,
        output=description.get("output", {}),
    )


@flow(task_runner=ConcurrentTaskRunner())
def main_flow(config_path=None, config_text=None):
    if config_text is None:
        if config_path is None:
            raise ValueError(f"Either config_path or config_text must be specified")
        with open(config_path, mode="r") as f:
            config_text = f.read()

    configuration = load_configuration(config_text)
    metadata = configuration["metadata"]
    data_queue = get_data_queue()

    data_futures = {}
    for data_obj in data_queue:
        dependencies = _parse_dependencies(
            data_futures=data_futures, parameters=data_obj.description["parameters"]
        )
        if isinstance(dependencies, list):
            future = _task.submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **{
                    f"_{index}": dependency
                    for index, dependency in enumerate(dependencies)
                },
            )
        elif isinstance(dependencies, dict):
            future = _task.submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **dependencies,
            )
        print("*" * 50)
        print(data_obj.name)
        data_futures[data_obj.name] = future

    return True
