import re
from importlib import import_module
from os import makedirs

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from .config import Data, get_data_queue, load_configuration
from .output import Output


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

    output_obj = Output(
        name=name, description=description.get("output", {}), metadata=metadata
    )

    # Load and return the output value if exists already
    if output_obj.exists:
        return output_obj.load()

    # Run the task to prepare the value
    caller = description["caller"]
    module_name, function_name = caller.split(":")
    module = import_module(module_name)
    func = getattr(module, function_name)

    if is_args(kwargs):
        value = func(*[v for v in kwargs.values()])
    else:
        value = func(**kwargs)

    # Write the value to the output path
    output_obj.dump(value)
    return value


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
