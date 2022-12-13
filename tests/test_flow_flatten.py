import pickle
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
            output:
                directory: "{output_directory}"
        task:
            task_a:
                caller: math:fabs
                parameters:
                    - -5
            task_b:
                caller: time:sleep
                parameters:
                    - 1
    """


def test_flow_flatten(output_directory, config_text):
    main_flow(config_text=config_text)
    task_a_path = fsjoin(output_directory, "task_a.pickle")
    task_b_path = fsjoin(output_directory, "task_b.pickle")
    assert exists(task_a_path)
    assert exists(task_b_path)
    with open(task_a_path, mode="rb") as fp:
        assert 5.0 == pickle.load(fp)
