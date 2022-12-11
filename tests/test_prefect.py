from time import sleep

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner


@task
def sleep_task():
    print("Sleeping...")
    sleep(5)
    return 1


@task
def wait_sleep_task(value):
    print(value)


@task
def print_task(value):
    print(value)


@flow(task_runner=ConcurrentTaskRunner())
def main():
    sleep_future = sleep_task.submit()
    print("Print sleep task")
    wait_sleep_task.submit(sleep_future)
    print("Print normal task")
    print_task.submit(2)


if __name__ == "__main__":
    main()
