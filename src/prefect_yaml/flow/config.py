from typing import Any, Dict, Optional

from ruamel.yaml import YAML

_DATA_CACHE = {}


class Data:

    yaml_tag = "!data"

    def __init__(self, name, description=None):
        self._name = name
        self._description = description

        global _DATA_CACHE
        if name not in _DATA_CACHE:
            _DATA_CACHE[name] = self

    @classmethod
    def create(cls, name):
        """
        Create a new data object.
        """
        global _DATA_CACHE
        if name in _DATA_CACHE:
            return _DATA_CACHE[name]

        obj = cls(name)
        _DATA_CACHE[name] = obj
        return obj

    @classmethod
    def from_yaml(cls, _, node):
        name = node.value
        return cls.create(name)

    @property
    def name(self) -> str:
        """
        Return the name of the data object.
        """
        return self._name

    @property
    def description(self) -> Dict:
        """
        Return the description of the data object.
        """
        return self._description

    def update_description(self, description: str) -> None:
        """
        Update the description of the data object.
        """
        self._description = description


def update_data_description(data: object):
    """
    Update the cached data iteratively.
    """
    global _DATA_CACHE
    tasks = data.get("task", {})
    for name, description in tasks.items():
        _DATA_CACHE[name].update_description(description)


def format_string(configuration: Dict[str, Any], variables: Dict[str, str]) -> object:
    if not variables:
        return configuration

    if isinstance(configuration, str):
        return configuration.format(**variables)
    elif isinstance(configuration, list):
        return [format_string(item, variables) for item in configuration]
    elif isinstance(configuration, dict):
        return {k: format_string(v, variables) for k, v in configuration.items()}

    return configuration


def load_configuration(
    configuration, variables: Optional[Dict[str, Any]] = None
) -> object:
    # Load the configuration from YAML format
    global _DATA_CACHE
    try:
        yaml = YAML()
        yaml.register_class(Data)
        configuration = yaml.load(configuration)
        configuration = format_string(configuration, variables)
        # Create the data object if it hasn't been depended
        for section in ["metadata", "task"]:
            if section not in configuration:
                raise RuntimeError(
                    f"Section `{section}` should be specified in the configuration. "
                    "For further details, please refer to the documentation "
                    "https://prefect-yaml.readthedocs.io/en/latest/configuration.html"
                )
        for task_name in configuration["task"]:
            Data.create(task_name)

        # Update the descriptions of all the data objects
        update_data_description(configuration)
        data_cache = _DATA_CACHE
    finally:
        _DATA_CACHE = {}
    return configuration, data_cache


def get_data_queue(data_cache):
    """
    Returns the data queue.
    """
    data_queue = []

    def _has_data(name):
        return any([d.name == name for d in data_queue])

    def _add_queue(data_obj):
        try:
            parameters = data_obj.description.get("parameters", {})
        except AttributeError as e:
            raise RuntimeError(
                "Description is not yet updated in data object "
                f"{data_obj.name}. Likely it is undefined. Please "
                "check your configuration to ensure the data object "
                f"is defined with caller. Error: {e}"
            )
        if isinstance(parameters, dict):
            parameters = parameters.values()

        for param_value in parameters:
            if isinstance(param_value, Data) and not _has_data(param_value.name):
                _add_queue(param_value)

        if not _has_data(data_obj.name):
            data_queue.append(data_obj)

    for data_obj in data_cache.values():
        _add_queue(data_obj)

    return data_queue
