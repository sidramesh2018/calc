import os
import sys
import subprocess
import traceback
import pexpect

MY_DIR = os.path.abspath(os.path.dirname(__file__))

SAUCE_CONNECT_SH_PATH = os.path.join(MY_DIR, 'sauce_connect.sh')

PROMPT = "BASH IS READY > "

TIMEOUT = 30  # In seconds.


def get_last_exitcode(child):
    child.sendline('echo $?')
    child.readline()
    exitcode = int(child.readline())
    child.expect(PROMPT)
    return exitcode


class SauceConnectTunnel:
    def __init__(self):
        self.child = None

    def safe_start(self):
        try:
            return self.start()
        except Exception:
            traceback.print_exc()
            return False

    def safe_stop(self):
        try:
            self.stop()
        except Exception:
            traceback.print_exc()

    def start(self):
        env = {}
        env.update(os.environ)
        env['PS1'] = PROMPT

        if sys.version_info < (3, 0):
            spawn = pexpect.spawn
        else:
            spawn = pexpect.spawnu

        child = spawn(
            '/bin/bash',
            ['--noprofile', '--norc'],
            env=env,
            timeout=TIMEOUT
            )

        child.logfile = sys.stdout

        child.expect(PROMPT)
        child.sendline('source {}'.format(SAUCE_CONNECT_SH_PATH))
        child.expect(PROMPT)
        child.sendline('travis_start_sauce_connect')
        child.expect(PROMPT)
        exitcode = get_last_exitcode(child)

        if exitcode == 0:
            self.child = child
            return True

        return False

    def stop(self):
        child = self.child
        self.child = None
        if child is not None:
            child.sendline('travis_stop_sauce_connect')
            child.expect(PROMPT)
            child.close()


def maybe_run_with_tunnel(args):
    env = {}
    env.update(os.environ)

    tunnel = SauceConnectTunnel()
    started = tunnel.safe_start()

    if started:
        print("Successfully established Sauce Connect tunnel. Amazing.")
    else:
        # Arg, Sauce Labs is likely being flaky, so just pretend like
        # we're in a non-Sauce environment.
        for key in ['SAUCE_USERNAME', 'SAUCE_ACCESS_KEY']:
            if key in env:
                del env[key]
        print("Establishing Sauce Connect tunnel failed. Whatever.")

    returncode = subprocess.call(
        args,
        env=env,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
        )

    tunnel.safe_stop()

    sys.exit(returncode)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("usage: {} <command>".format(sys.argv[0]))

    maybe_run_with_tunnel(sys.argv[1:])
