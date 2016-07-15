import os
import subprocess
import djclick as click


@click.command()
@click.option('--verbose', is_flag=True)
def command(verbose):
    '''
    Management command to test and lint everything
    '''
    click.echo('Running ALL THE TESTS')

    tests = [
        {'name': 'py.test', 'cmd': 'py.test'},
        {'name': 'flake8',  'cmd': 'flake8 --exclude=node_modules .'},
        {'name': 'eslint',  'cmd': 'npm run failable-eslint'},
    ]

    out = None
    if not verbose:
        out = open(os.devnull, 'w')

    for entry in tests:
        click.echo('-> {} '.format(entry['name']), nl=(out is None))
        entry['result'] = subprocess.call(
            entry['cmd'], stdout=out, stderr=subprocess.STDOUT, shell=True
        )
        if not verbose:
            if entry['result'] is 0:
                click.secho('OK', fg='green')
            else:
                click.secho('FAIL', fg='red')
