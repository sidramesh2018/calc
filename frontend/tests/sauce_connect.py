import os
import sys
import subprocess
import traceback
import pexpect

MY_DIR = os.path.abspath(os.path.dirname(__file__))

SAUCE_CONNECT_SH_PATH = os.path.join(MY_DIR, 'sauce_connect.sh')

LOAD_SAUCE_CONNECT = 'source {}'.format(SAUCE_CONNECT_SH_PATH)

PROMPT = "BASH IS READY > "

TIMEOUT = 30  # In seconds.


def get_last_exitcode(child):
    child.sendline('echo $?')
    child.readline()
    exitcode = int(child.readline())
    child.expect(PROMPT)
    return exitcode


class SauceConnectTunnel:
    def __init__(self, load_cmd=LOAD_SAUCE_CONNECT):
        self.load_cmd = load_cmd
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
        child.sendline(self.load_cmd)
        child.expect(PROMPT)
        child.sendline('travis_start_sauce_connect')
        child.expect(PROMPT)
        exitcode = get_last_exitcode(child)

        if exitcode == 0:
            self.child = child
            return True

        return False

    def stop(self):
        if self.child is None:
            return False

        self.child.sendline('travis_stop_sauce_connect')
        self.child.expect(PROMPT)
        exitcode = get_last_exitcode(self.child)

        if exitcode == 0:
            self.child.close()
            self.child = None
            return True

        return False


def maybe_run_with_tunnel(args, tunnel=None, env=os.environ):
    env = env.copy()

    if tunnel is None:
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
        stdout=sys.stdout,
        stderr=sys.stderr
        )

    tunnel.safe_stop()

    return returncode


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("usage: {} <command>".format(sys.argv[0]))

    sys.exit(maybe_run_with_tunnel(sys.argv[1:]))
