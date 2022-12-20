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
        object = data_obj.description.get("object")
        object_dep = (
            {
                "object": _parse_dependencies(
                    data_futures=data_futures,
                    parameters=object,
                )
            }
            if isinstance(object, Data)
            else {}
        )
        if isinstance(dependencies, list):
            dependencies = {
                **object_dep,
                **{
                    f"_{index}": dependency
                    for index, dependency in enumerate(dependencies)
                },
            }
        elif isinstance(dependencies, dict):
            dependencies = {
                **object_dep,
                **dependencies,
            }
        else:
            raise TypeError(
                "Dependencies must be in dict or list format, but "
                f"not {dependencies.__class__.__type__}"
            )
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
    if caller.startswith("object."):
        method_name = caller[7:]
        try:
            object = kwargs.pop("object")
        except KeyError:
            raise RuntimeError(
                "Failed to locate the object from dependencies in " f"task {name}"
            )
        try:
            func = getattr(object, method_name)
        except AttributeError:
            raise RuntimeError(
                f"Failed to get the method {method_name} from object "
                f"{object.__class__.__name__} in task {name}"
            )
    elif caller.count(":") == 1:
        module_name, function_name = caller.split(":")
        module = import_module(module_name)

        try:
            func = getattr(module, function_name)
        except AttributeError:
            raise RuntimeError(
                f"Failed to load function {function_name} from module {module_name} "
                f"in task {name}."
            )
    else:
        raise RuntimeError(
            f"Incorrect caller format {caller}. It should be either "
            "in `object.<method>` or `<module>:<function>`"
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


def _parse_dependencies(data_futures, parameters):
    if isinstance(parameters, Data):
        if parameters.name not in data_futures:
            raise ValueError(
                f"Value {parameters.name} should be in the data futures. "
                f"Current future list = {list(data_futures.keys())}"
            )
        return data_futures[parameters.name]
    elif isinstance(parameters, dict):
        return {
            key: _parse_dependencies(data_futures, value)
            for key, value in parameters.items()
        }
    elif isinstance(parameters, (tuple, set, list)):
        return [_parse_dependencies(data_futures, value) for value in parameters]

    return parameters
