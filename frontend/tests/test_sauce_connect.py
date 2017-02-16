import os
import sys
from unittest import TestCase

try:
    from .sauce_connect import SauceConnectTunnel, maybe_run_with_tunnel
except ModuleNotFoundError as e:
    # If we were run as a script, which is a valid use case for this
    # particular test suite, just let this pass; otherwise, it's
    # a failure!
    if __name__ != '__main__':
        raise e


def fakeloader(start_retval=0, stop_retval=0):
    return ("""\
        eval \"
        function travis_start_sauce_connect() {
          return %d
        }

        function travis_stop_sauce_connect() {
          return %d
        }\"
        """ % (start_retval, stop_retval)).strip()


class SauceConnectTunnelTests(TestCase):
    def test_stop_does_nothing_if_not_started(self):
        tun = SauceConnectTunnel()
        self.assertFalse(tun.stop())

    def test_start_returns_false_on_failure(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader(start_retval=1))
        self.assertFalse(tun.start())
        self.assertEqual(tun.child, None)

    def test_start_returns_true_on_success(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader())
        self.assertTrue(tun.start())
        self.assertTrue(tun.child is not None)

    def test_stop_returns_true_on_success(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader())
        tun.start()
        self.assertTrue(tun.stop())

    def test_stop_returns_false_on_failure(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader(stop_retval=1))
        tun.start()
        self.assertFalse(tun.stop())


class MaybeRunWithTunnelTests(TestCase):
    SAUCE_USERNAME_IS_BOOP = 15
    SAUCE_USERNAME_IS_NOT_BOOP = 16
    SAUCE_USERNAME_IS_NOT_PRESENT = 17

    @classmethod
    def run_as_script(cls):
        if 'SAUCE_USERNAME' not in os.environ:
            sys.exit(cls.SAUCE_USERNAME_IS_NOT_PRESENT)
        elif os.environ['SAUCE_USERNAME'] == 'boop':
            sys.exit(cls.SAUCE_USERNAME_IS_BOOP)
        else:
            sys.exit(cls.SAUCE_USERNAME_IS_NOT_BOOP)

    def _run(self, tunnel):
        return maybe_run_with_tunnel(
            [sys.executable, __file__],
            tunnel=tunnel,
            env=dict(SAUCE_USERNAME='boop')
            )

    def test_sauce_username_is_present_if_tunnel_established(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader(start_retval=0))
        self.assertEqual(self._run(tun), self.SAUCE_USERNAME_IS_BOOP)

    def test_sauce_username_is_absent_if_tunnel_failed(self):
        tun = SauceConnectTunnel(load_cmd=fakeloader(start_retval=1))
        self.assertEqual(self._run(tun), self.SAUCE_USERNAME_IS_NOT_PRESENT)


if __name__ == '__main__':
    MaybeRunWithTunnelTests.run_as_script()
