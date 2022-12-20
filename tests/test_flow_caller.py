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


def test_flow_object_caller(output_directory):
    config_text = """
    metadata:
      output:
        directory: "{output_directory}"
    task:
      task_a:
        caller: collections:UserList
        parameters:
          - "abcdabc"
      task_b:
        object: !data task_a
        caller: object.count
        parameters:
          - "a"
    """
    main_flow(config_text=config_text, variables={"output_directory": output_directory})
    task_a_path = fsjoin(output_directory, "task_a.pickle")
    task_b_path = fsjoin(output_directory, "task_b.pickle")
    assert exists(task_a_path)
    assert exists(task_b_path)
    with open(task_a_path, mode="rb") as fp:
        assert list("abcdabc") == pickle.load(fp)
    with open(task_b_path, mode="rb") as fp:
        assert 2 == pickle.load(fp)
