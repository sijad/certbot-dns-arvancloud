"""
Fakes needed for tests
"""

FAKE_API_TOKEN = 'XXXXXXXXXXXXXXXXXXXxxx'
FAKE_RECORD = {
    "record": {
        'id': "123Fake",
    }
}

FAKE_DOMAIN = 'some.domain'
FAKE_RECORD_ID = 'zzz'
FAKE_RECORD_NAME = 'thisisarecordname'

FAKE_RECORD_RESPONSE = {
    "id": FAKE_RECORD_ID,
    "name": "string",
}

FAKE_RECORDS_RESPONSE_WITH_RECORD = {
    "data": [
        {
            "id": FAKE_RECORD_ID,
            "name": FAKE_RECORD_NAME,
        }
    ]
}

FAKE_RECORDS_RESPONSE_WITHOUT_RECORD = {
    "data": [
    ]
}
