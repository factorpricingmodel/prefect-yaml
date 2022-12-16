from prefect import flow
from prefect.task_runners import ConcurrentTaskRunner

from .flow import prefect_yaml_flow as _flow


@flow(task_runner=ConcurrentTaskRunner())
def prefect_yaml_flow(
    config_path=None,
    config_text=None,
    variables=None,
):
    return _flow(
        config_path=config_path,
        config_text=config_text,
        variables=variables,
    )
