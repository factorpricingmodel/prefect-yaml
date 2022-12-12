import pickle
from math import sqrt
from os.path import exists
from os.path import join as fsjoin
from tempfile import TemporaryDirectory

import pytest

from prefect_yaml.flow import main_flow


@pytest.fixture
def output_directory():
    with TemporaryDirectory() as tmp:
        yield tmp


@pytest.fixture
def config_text(output_directory):
    return f"""
        metadata:
            output-directory: "{output_directory}"
        task:
            task_c:
                caller: math:sqrt
                parameters:
                    - !data task_b
            task_b:
                caller: math:fabs
                parameters:
                    - !data task_a
            task_a:
                caller: math:ceil
                parameters:
                    - -2.5
    """


def test_flow_deep(output_directory, config_text):
    main_flow(config_text=config_text)
    task_c_path = fsjoin(output_directory, "task_c.pickle")
    assert exists(task_c_path)
    with open(task_c_path, mode="rb") as fp:
        assert sqrt(2) == pickle.load(fp)
