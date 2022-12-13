import re
from importlib import import_module
from os.path import exists
from os.path import join as fsjoin
from typing import Any, Dict


class Output:
    """
    Output class.

    Each output object is constructed by the metadata and its
    output description. It supports checking its existence,
    reading and writing from / to the destinated directory.
    """

    def __init__(
        self, name: str, metadata: Dict[str, Any], description: Dict[str, Any]
    ):
        """
        Construct.

        Parameters
        ----------
        name: str
          Name of the output.
        metadata : dict
          Metadata.
        description : dict
          Output description.
        """
        self._name = name
        self._metadata = metadata
        self._description = description
        self._output_path = self._get_output_path(
            metadata=metadata,
            name=name,
            description=description,
        )

    @property
    def exists(self):
        """
        Return if the output exists.
        """
        return exists(self._output_path)

    @property
    def output_path(self):
        """
        Return the output path.
        """
        return self._output_path

    def load(self) -> Any:
        """
        Load the output.
        """
        output_format = self._description.get("format", "pickle")
        caller = self._description.get("load-caller")
        parameters = self._description.get("load-parameters", {})
        if caller is None:
            if output_format == "pickle":
                loader = Output._default_pickle_loader
            elif output_format == "json":
                loader = Output._default_json_loader
            else:
                raise ValueError(
                    f"Output format {output_format} does not have "
                    "default loader. Please define one with `load-caller` "
                    "instead"
                )
        elif ":" in caller:
            try:
                module_name, function_name = caller.split(":")
            except ValueError:
                raise ValueError(
                    f"Loader caller format {caller} is incorrect. "
                    "It should be formatted in <module>:<function>"
                )
            module = import_module(module_name)
            loader = getattr(module, function_name)
        else:
            raise ValueError(
                f"Customized loader caller {caller} is unrecognized. "
                "Please provide it either with the format of "
                "`<module>:<function>` or `object.<method>`"
            )

        try:
            return loader(self._output_path, **parameters)
        except Exception as e:  # noqa
            raise ValueError(
                f"Failed to load with format {output_format} and parameters "
                f"{parameters} from path {self._output_path}. Error: {e.message}"
            )

    def dump(self, value: Any):
        """
        Dump the output to the output path.

        Parameters
        ----------
        value: Any
          Dump the value to the output path.
        """
        output_format = self._description.get("format", "pickle")
        caller = self._description.get("dump-caller")
        parameters = self._description.get("dump-parameters", {})
        if caller is None:
            if output_format == "pickle":
                dumper = self._default_pickle_dumper
            elif output_format == "json":
                dumper = self._default_json_dumper
            else:
                raise ValueError(
                    f"Output format {output_format} does not have "
                    "default dumper. Please define one with `dump-caller` "
                    "instead"
                )
        elif re.match(r"^object\.(.*)$", caller):
            dumper_name = re.match(r"^object\.(.*)$", caller).groups()[0]
            try:
                dumper = lambda value, output_path, **kwargs: (  # noqa
                    getattr(value, dumper_name)(output_path, **kwargs)
                )
            except AttributeError:
                raise AttributeError(
                    f"Method {dumper_name} cannot be found in the value "
                    f"with type {value.__class__.__name__}"
                )
        elif ":" in caller:
            try:
                module_name, function_name = caller.split(":")
            except ValueError:
                raise ValueError(
                    f"Dumper caller format {caller} is incorrect. "
                    "It should be formatted in <module>:<function>"
                )
            module = import_module(module_name)
            dumper = getattr(module, function_name)
        else:
            raise ValueError(
                f"Customized dumper caller {caller} is unrecognized. "
                "Please provide it either with the format of "
                "`<module>:<function>` or `object.<method>`"
            )
        try:
            dumper(value, self._output_path, **parameters)
        except Exception as e:  # noqa
            raise ValueError(
                f"Failed to call the method {dumper_name} "
                f"with parameters {parameters}. Error: {e.message}"
            )

    @staticmethod
    def _get_output_path(metadata, name, description):
        output_directory = description.get(
            "output-directory", metadata["output-directory"]
        )
        output_name = description.get("name", name)
        output_format = description.get("format", "pickle")
        return fsjoin(output_directory, f"{output_name}.{output_format}")

    @staticmethod
    def _default_pickle_loader(output_path):
        from pickle import load as pickle_load  # nosec

        with open(output_path, mode="rb") as f:
            return pickle_load(f)

    @staticmethod
    def _default_json_loader(output_path):
        from json import load as json_load

        with open(output_path) as f:
            return json_load(f)

    @staticmethod
    def _default_pickle_dumper(value, output_path, **kwargs):
        from pickle import dump as pickle_dump  # nosec

        with open(output_path, mode="wb") as f:
            pickle_dump(value, f, **kwargs)

    @staticmethod
    def _default_json_dumper(value, output_path, **kwargs):
        from json import dump as json_dump

        with open(output_path, mode="w") as f:
            json_dump(value, f, **kwargs)
