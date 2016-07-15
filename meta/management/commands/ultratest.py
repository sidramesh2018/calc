import djclick as click
import subprocess


@click.command()
def command():
    click.echo('Running ALL THE TESTS')
    subprocess.call('py.test')
    subprocess.call('npm run eslint', shell=True)
