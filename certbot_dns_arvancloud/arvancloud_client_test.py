# pylint: disable=W0212
"""
Test suite for _ArvanCloudClient
"""
import unittest
import requests

import requests_mock

from certbot_dns_arvancloud.fakes import FAKE_API_TOKEN, FAKE_RECORD_RESPONSE, FAKE_DOMAIN, \
    FAKE_RECORD_ID, FAKE_RECORDS_RESPONSE_WITH_RECORD, FAKE_RECORD_NAME, FAKE_RECORDS_RESPONSE_WITHOUT_RECORD
from certbot_dns_arvancloud.arvancloud_client import ARVANCLOUD_API_ENDPOINT, \
    _MalformedResponseException, _NotAuthorizedException, _RecordNotFoundException


class ArvanCloudClientTest(unittest.TestCase):
    record_name = 'foo'
    record_content = 'bar'
    record_ttl = 42

    def setUp(self):
        from certbot_dns_arvancloud.dns_arvancloud import _ArvanCloudClient  # pylint: disable=import-outside-toplevel
        self.client = _ArvanCloudClient(FAKE_API_TOKEN)

    def test_add_record(self):
        with requests_mock.Mocker() as mock:
            mock.post('{0}/{1}/dns-records'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN), status_code=200, json=FAKE_RECORD_RESPONSE)
            response = self.client.add_record(FAKE_DOMAIN, "TXT", "somename", "somevalue", 42, False)
            self.assertEqual(response, FAKE_RECORD_RESPONSE)

    def test_add_record_but_record_creation_not_200(self):
        with requests_mock.Mocker() as mock:
            mock.post('{0}/{1}/dns-records'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN), status_code=422)
            self.assertRaises(
                _MalformedResponseException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42, False
            )

    def test_add_record_but_unauthorized(self):
        with requests_mock.Mocker() as mock:
            mock.post('{0}/{1}/dns-records'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN), status_code=401)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42, False
            )

    def test_add_record_but_records_listing_times_out(self):
        with requests_mock.Mocker() as mock:
            mock.post('{0}/{1}/dns-records'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN), exc=requests.ConnectTimeout)
            self.assertRaises(
                requests.ConnectionError,
                self.client.add_record, FAKE_DOMAIN, "TXT", "somename", "somevalue", 42, False
            )

    def test_delete_record(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/{1}/dns-records/{2}'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN, FAKE_RECORD_ID), status_code=200)
            self.client.delete_record(FAKE_DOMAIN, FAKE_RECORD_ID)

    def test_delete_but_authorization_fails(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/{1}/dns-records/{2}'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN, FAKE_RECORD_ID), status_code=401)
            self.assertRaises(
                _NotAuthorizedException,
                self.client.delete_record, FAKE_DOMAIN, FAKE_RECORD_ID
            )

    def test_delete_record_but_deletion_is_404(self):
        with requests_mock.Mocker() as mock:
            mock.delete('{0}/{1}/dns-records/{2}'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN, FAKE_RECORD_ID), status_code=404)
            self.assertRaises(
                _MalformedResponseException,
                self.client.delete_record, FAKE_DOMAIN, FAKE_RECORD_ID
            )

    def test_delete_record_by_name_and_found(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/{1}/dns-records?search={2}'.format(
                ARVANCLOUD_API_ENDPOINT,
                FAKE_DOMAIN,
                FAKE_RECORD_NAME
            ), status_code=200, json=FAKE_RECORDS_RESPONSE_WITH_RECORD)
            mock.delete('{0}/{1}/dns-records/{2}'.format(ARVANCLOUD_API_ENDPOINT, FAKE_DOMAIN, FAKE_RECORD_ID), status_code=200)
            self.client.delete_record_by_name(FAKE_DOMAIN, FAKE_RECORD_NAME)

    def test_delete_record_by_name_but_its_not_found(self):
        with requests_mock.Mocker() as mock:
            mock.get('{0}/{1}/dns-records?search={2}'.format(
                ARVANCLOUD_API_ENDPOINT,
                FAKE_DOMAIN,
                FAKE_RECORD_NAME
            ), status_code=200, json=FAKE_RECORDS_RESPONSE_WITHOUT_RECORD)
            self.assertRaises(
                _RecordNotFoundException,
                self.client.delete_record_by_name, FAKE_DOMAIN, FAKE_RECORD_NAME
            )
