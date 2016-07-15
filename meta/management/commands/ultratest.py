import djclick as click


@click.command()
def command():
    click.secho('Running ALL THE TESTS')
