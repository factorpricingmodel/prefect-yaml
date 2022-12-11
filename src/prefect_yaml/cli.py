import click


@click.command()
@click.option(
    "--configuration",
    "-c",
    required=True,
)
def run(configuration):
    """
    Run the prefect flow.
    """
