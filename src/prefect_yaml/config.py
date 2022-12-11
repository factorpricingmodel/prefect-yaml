from typing import Dict

from ruamel.yaml import YAML


class Data:

    yaml_tag = "!data"

    _DATA_MAPPING = {}

    def __init__(self, name, description=None, submitted=False, future=None):
        self._name = name
        self._description = description
        self._submitted = submitted
        self._future = future
        if name not in Data._DATA_MAPPING:
            Data._DATA_MAPPING[name] = self

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the data cache.
        """
        cls._DATA_MAPPING = {}

    @classmethod
    def create(cls, name):
        """
        Create a new data object.
        """
        if name in cls._DATA_MAPPING:
            return cls._DATA_MAPPING[name]

        obj = cls(name)
        cls._DATA_MAPPING[name] = obj
        return obj

    @classmethod
    def from_yaml(cls, _, node):
        name = node.value
        return cls.create(name)

    @classmethod
    def get(cls, name: str) -> object:
        """
        Get the data from the cache.
        """
        return Data._DATA_MAPPING[name]

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

    @property
    def submitted(self) -> bool:
        """
        Return whether the data object is submitted.
        """
        return self._submitted

    @property
    def future(self) -> object:
        """
        Return the future of the data object.
        """
        return self._future

    def update_description(self, description: str) -> None:
        """
        Update the description of the data object.
        """
        self._description = description


def update_data(data: object) -> object:
    """
    Update the cached data iteratively.
    """
    if isinstance(data, list):
        return [update_data(item) for item in data]
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in Data._DATA_MAPPING:
                Data._DATA_MAPPING[key].update_description(value)
        return {key: update_data(value) for key, value in data.items()}
    else:
        return data


def load_configuration(configuration):
    # Clear the data cache first
    Data.clear_cache()
    # Load the configuration from YAML format
    yaml = YAML()
    yaml.register_class(Data)
    configuration = yaml.load(configuration)
    # Create the data object if it hasn't been depended
    for task_name in configuration["task"]:
        Data.create(task_name)
    # Update the descriptions of all the data objects
    configuration = update_data(configuration)
    return configuration


def get_data_queue():
    """
    Returns the data queue.
    """
    data_queue = []

    def _has_data(name):
        return any([d.name == name for d in data_queue])

    def _add_queue(data_obj):
        parameters = data_obj.description.get("parameters", {})
        if isinstance(parameters, dict):
            parameters = parameters.values()

        for param_value in parameters:
            if isinstance(param_value, Data) and not _has_data(param_value.name):
                _add_queue(param_value)

        if not _has_data(data_obj.name):
            data_queue.append(data_obj)

    for data_obj in Data._DATA_MAPPING.values():
        _add_queue(data_obj)

    return data_queue
