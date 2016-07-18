import os
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
        # {'name': 'py.test', 'cmd': 'py.test'},
        {'name': 'flake8',  'cmd': 'flake8 --exclude=node_modules .'},
        {'name': 'eslint',  'cmd': 'npm run failable-eslint'},
    ]

    is_verbose = verbosity > 1

    out = None
    if not is_verbose:
        out = open(os.devnull, 'w')

    for entry in tests:
        echo('-> {} '.format(entry['name']), 1, nl=is_verbose)

        echo('Running "{}"'.format(entry['cmd']), 2)

        entry['result'] = subprocess.call(
            entry['cmd'], stdout=out, stderr=subprocess.STDOUT, shell=True
        )

        if not is_verbose:
            if entry['result'] is 0:
                echo('OK', 1, fg='green')
            else:
                echo('FAIL', 1, fg='red')
