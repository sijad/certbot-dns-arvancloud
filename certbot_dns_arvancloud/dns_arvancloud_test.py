"""Tests for certbot_dns_ispconfig.dns_ispconfig."""

import unittest

import mock

from certbot.compat import os
from certbot.errors import PluginError
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

from certbot_dns_arvancloud.fakes import FAKE_API_TOKEN, FAKE_RECORD

class AuthenticatorTest(
        test_util.TempDirTestCase,
        dns_test_common.BaseAuthenticatorTest
):
    """
    Test for ArvanCloud DNS Authenticator
    """
    def setUp(self):
        super(AuthenticatorTest, self).setUp()
        from certbot_dns_arvancloud.dns_arvancloud import Authenticator  # pylint: disable=import-outside-toplevel

        path = os.path.join(self.tempdir, 'fake_credentials.ini')
        dns_test_common.write(
            {
                'arvancloud_api_token': FAKE_API_TOKEN,
            },
            path,
        )

        super(AuthenticatorTest, self).setUp()
        self.config = mock.MagicMock(
            arvancloud_credentials=path, arvancloud_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, 'arvancloud')

        self.mock_client = mock.MagicMock()
        # _get_ispconfig_client | pylint: disable=protected-access
        self.auth._get_arvancloud_client = mock.MagicMock(return_value=self.mock_client)

    def test_perform(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        self.auth.perform([self.achall])
        self.mock_client.add_record.assert_called_with(
            DOMAIN, 'TXT', '_acme-challenge.' + DOMAIN + '.', mock.ANY, mock.ANY
        )

    def test_cleanup(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.delete_record_by_name.assert_called_with(DOMAIN, '_acme-challenge.' + DOMAIN + '.')

    def test_cleanup_but_connection_aborts(self):
        self.mock_client.add_record.return_value = FAKE_RECORD
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.perform([self.achall])
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        self.mock_client.delete_record_by_name.assert_called_with(DOMAIN, '_acme-challenge.' + DOMAIN + '.')


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
