from os.path import join as fsjoin

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from .config import Data


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
        raise TypeError("Parameters type {parameters} is not supported")

    return dependencies


@task
def _task(name, description, metadata, *args, **kwargs):
    output_directory = metadata["output-directory"]
    file_format = description.get("file-format", "pickle")
    output_name = description.get("output-name", f"{name}.{file_format}")
    file_path = fsjoin(output_directory, output_name)
    with open(file_path, "w+") as f:
        f.write("")


@flow(task_runner=ConcurrentTaskRunner())
def main_flow(metadata, data_queue):
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
                *dependencies,
            )
        elif isinstance(dependencies, dict):
            future = _task.submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **dependencies,
            )
        data_futures[data_obj.name] = future

    return True
