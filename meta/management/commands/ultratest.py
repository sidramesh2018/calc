import djclick as click
import subprocess


@click.command()
def command():
    click.secho('Running ALL THE TESTS')
    subprocess.call("py.test")
