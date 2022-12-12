import re
from importlib import import_module
from os import makedirs
from os.path import exists
from os.path import join as fsjoin

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from .config import Data, get_data_queue, load_configuration


@flow(task_runner=ConcurrentTaskRunner())
def main_flow(config_path=None, config_text=None):
    if config_text is None:
        if config_path is None:
            raise ValueError("Either config_path or config_text must be specified")
        with open(config_path) as f:
            config_text = f.read()

    configuration, data_cache = load_configuration(config_text)
    data_queue = get_data_queue(data_cache)
    metadata = configuration["metadata"]

    # Prepare the directory
    output_directory = metadata["output-directory"]
    makedirs(output_directory, exist_ok=True)

    # Submit each task by dependency order
    data_futures = {}
    for data_obj in data_queue:
        parameters = data_obj.description.get("parameters", {})
        dependencies = _parse_dependencies(
            data_futures=data_futures,
            parameters=parameters,
        )
        if isinstance(dependencies, list):
            future = run_task.submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **{
                    f"_{index}": dependency
                    for index, dependency in enumerate(dependencies)
                },
            )
        elif isinstance(dependencies, dict):
            future = run_task.submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **dependencies,
            )
        data_futures[data_obj.name] = future

    return True


@task
def run_task(name, description, metadata, **kwargs):
    def is_args(kwargs):
        return all([re.match(r"^_\d+$", k) is not None for k in kwargs.keys()])

    output = description.get("output", {})
    if _exists_output(metadata=metadata, name=name, output=output):
        return _load_output(metadata=metadata, name=name, output=output)
    caller = description["caller"]
    module_name, function_name = caller.split(":")
    module = import_module(module_name)
    func = getattr(module, function_name)

    if is_args(kwargs):
        value = func(*[v for v in kwargs.values()])
    else:
        value = func(**kwargs)

    return _export_output(
        metadata=metadata,
        name=name,
        value=value,
        output=output,
    )


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


def _get_output_path(metadata, name, output):
    output_directory = metadata["output-directory"]
    output_name = output.get("name", name)
    output_format = output.get("format", "pickle")
    return fsjoin(output_directory, f"{output_name}.{output_format}")


def _exists_output(metadata, name, output):
    return exists(_get_output_path(metadata=metadata, name=name, output=output))


def _load_output(metadata, name, output):
    output_format = output.get("format", "pickle")
    output_path = _get_output_path(metadata=metadata, name=name, output=output)
    if output_format == "pickle":
        from pickle import load as pickle_load  # nosec

        with open(output_path, mode="rb") as f:
            return pickle_load(f)
    elif output_format == "json":
        from json import load as json_load

        with open(output_path) as f:
            return json_load(f)
    else:
        raise ValueError(f"Output format {output_format} is not supported")


def _export_output(metadata, name, value, output):
    output_format = output.get("format", "pickle")
    output_path = _get_output_path(metadata=metadata, name=name, output=output)
    if output_format == "pickle":
        from pickle import dump as pickle_dump  # nosec

        with open(output_path, mode="wb") as f:
            pickle_dump(value, f)
    elif output_format == "json":
        from json import dump as json_dump

        with open(output_path, mode="w") as f:
            json_dump(value, f)
    else:
        raise ValueError(f"Output format {output_format} is not supported")

    return value
