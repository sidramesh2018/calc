import os
import sys
import subprocess
import djclick as click


@click.command()
@click.pass_verbosity
def command(verbosity):
    '''
    Management command to test and lint everything
    '''

    def echo(msg, v_level, **kwargs):
        if verbosity < v_level:
            return
        click.secho(msg, **kwargs)

    echo('Running ALL THE TESTS', 1)

    tests = [
        {'name': 'flake8',  'cmd': 'flake8 --exclude=node_modules .'},
        {'name': 'eslint',  'cmd': 'npm run failable-eslint'},
        {'name': 'py.test', 'cmd': 'py.test'},
    ]

    is_verbose = verbosity > 1

    out = None
    if not is_verbose:
        out = open(os.devnull, 'w')

    failing_tests = []
    for entry in tests:
        echo('-> {} '.format(entry['name']), 1, nl=is_verbose)

        echo('Running "{}"'.format(entry['cmd']), 2)

        result = subprocess.call(
            entry['cmd'], stdout=out, stderr=subprocess.STDOUT, shell=True
        )

        if result is not 0:
            failing_tests.append(entry['name'])

        if not is_verbose:
            if result is 0:
                echo('OK', 1, fg='green')
            else:
                echo('FAIL', 1, fg='red')

    if len(failing_tests) > 0:
        echo('Failing tests: {}'.format(', '.join(failing_tests)), 0)
        sys.exit(1)
