import re
from importlib import import_module

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner

from .config import Data, get_data_queue, load_configuration
from .output import Output


def main_flow(
    config_path=None,
    config_text=None,
    variables=None,
    name=None,
):
    """
    Main flow entry point.
    """
    return flow(prefect_yaml_flow, task_runner=ConcurrentTaskRunner(), name=name)(
        config_path=config_path,
        variables=variables,
        config_text=config_text,
    )


def prefect_yaml_flow(config_path=None, config_text=None, variables=None):
    """
    Prefect YAML flow function.
    """
    if config_text is None:
        if config_path is None:
            raise ValueError("Either config_path or config_text must be specified")
        with open(config_path) as f:
            config_text = f.read()

    configuration, data_cache = load_configuration(config_text, variables)
    data_queue = get_data_queue(data_cache)
    metadata = configuration["metadata"]

    # Submit each task by dependency order
    data_futures = {}
    for data_obj in data_queue:
        parameters = data_obj.description.get("parameters", {})
        dependencies = _parse_dependencies(
            data_futures=data_futures,
            parameters=parameters,
        )
        if isinstance(dependencies, list):
            future = task(run_task, name=data_obj.name).submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **{
                    f"_{index}": dependency
                    for index, dependency in enumerate(dependencies)
                },
            )
        elif isinstance(dependencies, dict):
            future = task(run_task, name=data_obj.name).submit(
                name=data_obj.name,
                description=data_obj.description,
                metadata=metadata,
                **dependencies,
            )
        data_futures[data_obj.name] = future

    return True


def run_task(name, description, metadata, **kwargs):
    def is_args(kwargs):
        return all([re.match(r"^_\d+$", k) is not None for k in kwargs.keys()])

    output_description = {
        **metadata.get("output", {}),
        **description.get("output", {}),
    }
    output_obj = Output(name=name, description=output_description)

    # Load and return the output value if exists already
    if output_obj.exists:
        return output_obj.load()

    # Run the task to prepare the value
    try:
        caller = description["caller"]
    except KeyError:
        raise RuntimeError(
            f"Task {name} does not have any caller but it does not "
            f"exist in the path {output_obj.output_path}."
        )
    module_name, function_name = caller.split(":")
    module = import_module(module_name)

    try:
        func = getattr(module, function_name)
    except AttributeError:
        raise RuntimeError(
            f"Failed to load function {function_name} from module {module_name} "
            f"in task {name}."
        )

    try:
        if is_args(kwargs):
            value = func(*[v for v in kwargs.values()])
        else:
            value = func(**kwargs)
    except TypeError as error:
        raise RuntimeError(
            f"Failed to run caller {caller} with parameters {kwargs} in "
            f"task {name}. Exception: {error}"
        )

    # Write the value to the output path
    return output_obj.dump(value)


def _parse_dependencies(data_futures, parameters, allow_primitive=False):
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
            elif isinstance(value, (list, tuple, dict)):
                dependencies[key] = _parse_dependencies(
                    data_futures, value, allow_primitive=True
                )
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
            elif isinstance(value, (list, tuple, dict)):
                dependencies.append(
                    _parse_dependencies(data_futures, value, allow_primitive=True)
                )
            else:
                dependencies.append(value)
    elif not allow_primitive:
        raise TypeError("Parameters type {parameters} is not supported")

    return dependencies
