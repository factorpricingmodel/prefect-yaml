from typing import Dict, Any
from os.path import join as fsjoin, exists


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

    def load(self) -> Any:
        """
        Load the output.
        """
        output_format = self._description.get("format", "pickle")
        if output_format == "pickle":
            from pickle import load as pickle_load  # nosec

            with open(self._output_path, mode="rb") as f:
                return pickle_load(f)
        elif output_format == "json":
            from json import load as json_load

            with open(self._output_path) as f:
                return json_load(f)
        else:
            raise ValueError(f"Output format {output_format} is not supported")

    def dump(self, value: Any):
        """
        Dump the output to the output path.

        Parameters
        ----------
        value: Any
          Dump the value to the output path.
        """
        output_format = self._description.get("format", "pickle")
        if output_format == "pickle":
            from pickle import dump as pickle_dump  # nosec

            with open(self._output_path, mode="wb") as f:
                pickle_dump(value, f)
        elif output_format == "json":
            from json import dump as json_dump

            with open(self._output_path, mode="w") as f:
                json_dump(value, f)
        else:
            raise ValueError(f"Output format {output_format} is not supported")

    @staticmethod
    def _get_output_path(metadata, name, description):
        output_directory = metadata["output-directory"]
        output_name = description.get("name", name)
        output_format = description.get("format", "pickle")
        return fsjoin(output_directory, f"{output_name}.{output_format}")
