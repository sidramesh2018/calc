import os
import sys
import subprocess
import djclick as click


@click.command()
@click.pass_verbosity
@click.option('--lintonly', help='Run linters only (no tests)', is_flag=True)
def command(verbosity, lintonly):
    '''
    Management command to test and lint everything
    '''
    linters = [
        {
            'name': 'flake8',
            'cmd': 'flake8 --exclude=node_modules .'
        },
        {
            'name': 'eslint',
            'cmd': 'npm run failable-eslint'
        },
    ]

    tests = [
        {
            'name': 'py.test',
            'cmd': 'py.test'
        },
    ]

    def echo(msg, v_level, **kwargs):
        if verbosity < v_level:
            return
        click.secho(msg, **kwargs)

    is_verbose = verbosity > 1

    if lintonly:
        echo('Running linters only', 1)
    else:
        echo('Running ALL THE TESTS', 1)

    out = None
    if not is_verbose:
        out = open(os.devnull, 'w')

    to_run = linters
    if not lintonly:
        to_run += tests

    failures = []
    for entry in to_run:
        echo('-> {} '.format(entry['name']), 1, nl=is_verbose)

        echo('Running "{}"'.format(entry['cmd']), 2)

        result = subprocess.call(
            entry['cmd'], stdout=out, stderr=subprocess.STDOUT, shell=True
        )

        if result is not 0:
            failures.append(entry['name'])

        if not is_verbose:
            if result is 0:
                echo('OK', 1, fg='green')
            else:
                echo('FAIL', 1, fg='red')

    if len(failures) > 0:
        echo('Failing tests: {}'.format(', '.join(failures)), 0)
        sys.exit(1)
