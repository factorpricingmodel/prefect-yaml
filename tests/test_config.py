import pytest

from prefect_yaml.flow.config import get_data_queue, load_configuration


@pytest.fixture
def deep_config():
    return """
    metadata:
        output:
            directory: "output"
    task:
      task_c:
        output-name: "task_c.pickle"
        caller: "task_c:run"
        parameters:
          input: !data task_b
      task_b:
        output-name: "task_b.pickle"
        caller: "task_b:run"
        parameters:
          input: !data task_a
      task_a:
        output-name: "task_a.pickle"
        caller: "task_a:run"
    """


@pytest.fixture
def sparse_config():
    return """
    metadata:
        output:
            directory: "output"
    task:
      task_d:
        output-name: "task_c.pickle"
        caller: "task_c:run"
        parameters:
          input_1: !data task_b
          input_2: !data task_a
          input_3: !data task_c
      task_c:
        output-name: "task_c.pickle"
        caller: "task_c:run"
      task_b:
        output-name: "task_b.pickle"
        caller: "task_b:run"
        parameters:
          input: !data task_a
      task_a:
        output-name: "task_a.pickle"
        caller: "task_a:run"
    """


def test_load_configuration(deep_config):
    parsed_config, data_cache = load_configuration(deep_config)
    assert parsed_config["task"]["task_c"]["parameters"]["input"].name == "task_b"
    assert parsed_config["task"]["task_b"]["parameters"]["input"].name == "task_a"
    assert data_cache.get("task_a").description["output-name"] == "task_a.pickle"
    assert data_cache.get("task_b").description["output-name"] == "task_b.pickle"
    assert data_cache.get("task_c").description["output-name"] == "task_c.pickle"


def test_get_data_queue_deep_config(deep_config):
    _, data_cache = load_configuration(deep_config)
    data_queue = get_data_queue(data_cache)
    assert ["task_a", "task_b", "task_c"] == [d.name for d in data_queue]


def test_get_data_queue_sparse_config(sparse_config):
    _, data_cache = load_configuration(sparse_config)
    data_queue = get_data_queue(data_cache)
    assert ["task_a", "task_b", "task_c", "task_d"] == [d.name for d in data_queue]
