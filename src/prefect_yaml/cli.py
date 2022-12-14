import click

from .flow import main_flow


@click.command()
@click.option(
    "--configuration",
    "-c",
    required=True,
    help="Configuration file path",
)
@click.option(
    "--variable",
    "-v",
    "variables",
    multiple=True,
    help=(
        "Variable of which its key and value are split by equal side. "
        "For example, key=value"
    ),
)
def main(configuration, variables):
    """
    Run the prefect flow.
    """
    variables = variables or []
    variables = dict([variable.split("=") for variable in variables])
    main_flow(config_path=configuration, variables=variables)
