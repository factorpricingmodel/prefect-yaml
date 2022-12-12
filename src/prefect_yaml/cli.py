import click

from .flow import main_flow


@click.command()
@click.option(
    "--configuration",
    "-c",
    required=True,
)
def main(configuration):
    """
    Run the prefect flow.
    """
    main_flow(config_path=configuration)
