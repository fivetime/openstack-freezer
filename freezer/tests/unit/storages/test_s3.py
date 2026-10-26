# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import unittest
from unittest import mock

from freezer.storage import s3


class FakeS3Objects(object):

    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Body, Key, ContentLength):
        self.objects[(Bucket, Key)] = Body.encode()

    def get_object(self, Bucket, Key):
        return {'Body': io.BytesIO(self.objects[(Bucket, Key)])}


class TestS3StorageStreamHeaders(unittest.TestCase):

    def _storage(self, container):
        storage = s3.S3Storage('access', 'secret', 'http://s3', container,
                               1024, skip_prepare=True)
        connection = FakeS3Objects()
        storage.get_s3_connection = mock.Mock(return_value=connection)
        storage.upload_stream = mock.Mock()
        return storage

    def test_get_stream_headers(self):
        for container in ('bucket', 'bucket/prefix'):
            storage = self._storage(container)
            headers = {'x-object-meta-length': '4',
                       'x-object-meta-freezer-backup-id': 'b1'}
            storage.add_stream([b'data'], 'vol1/1463018422', headers=headers)
            self.assertEqual(headers,
                             storage.get_stream_headers('vol1/1463018422'))
