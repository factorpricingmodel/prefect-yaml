from os.path import exists
from os.path import join as fsjoin
from tempfile import TemporaryDirectory

import pytest

from prefect_yaml.config import get_data_queue, load_configuration
from prefect_yaml.flow import main_flow


@pytest.fixture
def configuration():
    with TemporaryDirectory() as tmp:
        yield f"""
            metadata:
                output-directory: "{tmp}"
            task:
                task_a:
                    caller: abs
                    parameters:
                      - -5
                task_b:
                    caller: time:sleep
                    parameters:
                      - 1
        """


def test_flow_flatten(configuration):
    configuration = load_configuration(configuration)
    data_queue = get_data_queue()
    main_flow(configuration["metadata"], data_queue)

    output_directory = configuration["metadata"]["output-directory"]
    assert exists(fsjoin(output_directory, "task_a.pickle"))
    assert exists(fsjoin(output_directory, "task_b.pickle"))
