"""
A ArvanCloud helper class to wrap the API relevant for the functionality in this plugin
"""
import json
import requests

ARVANCLOUD_API_ENDPOINT = 'https://napi.arvancloud.com/cdn/4.0/domains/'


class _ArvanCloudException(Exception):
    pass

class _MalformedResponseException(_ArvanCloudException):
    def __init__(self, cause, *args):
        super(_MalformedResponseException, self).__init__(
            'Received an unexpected response from ArvanCloud API:\n{0}'.format(cause), *args)
        self.cause = cause


class _RecordNotFoundException(_ArvanCloudException):
    def __init__(self, record_name, *args):
        super(_RecordNotFoundException, self).__init__('Record with name {0} not found'.format(record_name), *args)
        self.record_name = record_name


class _NotAuthorizedException(_ArvanCloudException):
    def __init__(self, *args):
        super(_NotAuthorizedException, self).__init__('Malformed authorization or invalid API token', *args)


class _ArvanCloudClient:
    """
    A little helper class for operations on the ArvanCloud DNS API
    """

    def __init__(self, token):
        """
        Initialize client by providing a ArvanCloud DNS API token
        :param token: ArvanCloud DNS API Token retrieved from: https://npanel.arvancloud.com/profile/api-keys
        """
        self.token = token

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": self.token,
        }

    def add_record(self, domain, record_type, name, value, ttl, cloud):  # pylint: disable=too-many-arguments
        """
        API call to add record to ``domain`` in your ArvanCloud Account, while specifying ``record_type``,
        ``name``, ``value`` and ``ttl``
        :param domain: Domain to determine where record should be added
        :param record_type: A valid DNS record type
        :param name: Full record name
        :param value: Record value
        :param ttl: Time to live
        :param cloud: Cloud flag
        :raises ._MalformedResponseException: If the response is missing expected values or is invalid JSON
        :raises ._NotAuthorizedException: If ArvanCloud does not accept the authorization credentials
        :raises requests.exceptions.ConnectionError: If the API request fails
        """
        create_record_response = requests.post(
            url="{0}/{1}/dns-records".format(ARVANCLOUD_API_ENDPOINT, domain),
            headers=self._headers,
            data=json.dumps({
                "type": record_type,
                "name": name,
                "value": value,
                "ttl": ttl,
                "cloud": cloud
            })
        )
        if create_record_response.status_code == 401:
            raise _NotAuthorizedException()
        try:
            return create_record_response.json()
        except (ValueError, UnicodeDecodeError) as exception:
            raise _MalformedResponseException(exception)

    def delete_record_by_name(self, domain, record_name):
        """
        Searches for a matching ``domain``, if found find and delete a record matching ``record_name`
        Deletes record with ``record_id`` from your ArvanCloud Account
        :param domain: Domain of the record should be found
        :param record_name: ID of record to be deleted
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._MalformedResponseException: If the API response is not 200
        :raises ._RecordNotFoundException: If no record is found matching ``record_name``
        :raises ._NotAuthorizedException: If ArvanCloud does not accept the authorization credentials
        """
        record_id = self._get_record_id_by_name(domain, record_name)
        self.delete_record(domain, record_id)

    def delete_record(self, domain, record_id):
        """
        Deletes record with ``record_id`` from your ArvanCloud Account
        :param domain: Domain of the record
        :param record_id: ID of record to be deleted
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._MalformedResponseException: If the API response is not 200
        :raises ._NotAuthorizedException: If ArvanCloud does not accept the authorization credentials
        """
        response = requests.delete(
            url="{0}/{1}/dns-records/{2}".format(ARVANCLOUD_API_ENDPOINT, domain, record_id), # why would you pass domain along with record id I wonder
            headers=self._headers
        )
        if response.status_code == 401:
            raise _NotAuthorizedException()
        if response.status_code != 200:
            raise _MalformedResponseException('Status code not 200')

    def _get_record_id_by_name(self, domain, record_name):
        """
        :param domain: Domain name where the record should be searched
        :param record_name: Name of the record that is searched
        :return: The ID of the record with name ``record_name`` if found
        :raises ._MalformedResponseException: If the response is missing expected values or is invalid JSON
        :raises requests.exceptions.ConnectionError: If the API request fails
        :raises ._NotAuthorizedException: If ArvanCloud does not accept the authorization credentials
        :rtype: str
        """
        records_response = requests.get(
            url="{0}/{1}/dns-records".format(ARVANCLOUD_API_ENDPOINT, domain),
            params={
                'search': record_name,
            },
            headers=self._headers
        )
        if records_response.status_code == 401:
            raise _NotAuthorizedException()
        try:
            records = records_response.json()['data']
            if len(records) > 0:
                return records[0]['id']
        except (ValueError, UnicodeDecodeError, KeyError) as exception:
            raise _MalformedResponseException(exception)
        raise _RecordNotFoundException(record_name)
