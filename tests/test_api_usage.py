import unittest
from pymdc.api.users import Users
from pymdc.api.buckets import Bucket, Buckets
from pymdc.api.keys import Keys
from pymdc.keypair import ECDSA
from pymdc.rest import REST
import os
import tempfile
import time

class TestAPIUsage(unittest.TestCase):
    def test_api_usage(self):
        # Test user registration + activation.
        user = Users("matthew10@coinbend.com", "password")
        ret = user.register()["error"]
        self.assertTrue("already" in ret)
        ret = user.activate("test")["error"]
        self.assertTrue("Invalid" in ret)

        # Create new key.
        key_pair = ECDSA()
        keys = Keys(user)
        ret = keys.create(key_pair)["key"]
        self.assertTrue(key_pair.get_public_key() in ret)

        # Check it exists.
        ret = keys.list()
        found = False
        for result in ret:
            if key_pair.get_public_key() in result["key"]:
                found = True
                break
        self.assertTrue(found)

        # Delete the key.
        keys.delete(key_pair)

        # Check its been deleted.
        ret = keys.list()
        found = False
        for result in ret:
            if key_pair.get_public_key() in result["key"]:
                found = True
                break
        self.assertFalse(found)

        # Add the key back now.
        keys.create(key_pair)

        # Test buckets stuff.
        buckets = Buckets(key_pair)
        bucket_name = str(time.time())
        bucket_id = buckets.create(bucket_name, 10, 10, [key_pair])["id"]
        self.assertTrue(bucket_id)
        found = False
        for result in buckets.list():
            if bucket_id in result["id"]:
                found = True
                break
        self.assertTrue(found)

        # Test bucket commands.
        bucket = Bucket(bucket_id, key_pair)
        bucket_name = str(time.time())
        self.assertTrue(bucket_name in bucket.patch({"name": bucket_name})["name"])
        bucket.delete()
        self.assertTrue("not found" in bucket.list()["error"])
        bucket_id = buckets.create(bucket_name, 10, 10, [key_pair])["id"]
        bucket = Bucket(bucket_id, key_pair)

        # Test file upload.
        token = bucket.files.token("PUSH")["token"]
        content = os.urandom(1024 * 1024 * 1)
        handle, path = tempfile.mkstemp()
        with open(path, "wb") as fp:
            fp.write(content)
        file_hash = bucket.files.upload(path, token)["hash"]
        found = False
        for result in bucket.files.list():
            if file_hash in result["hash"]:
                found = True
                break
        self.assertTrue(found)

        # Cleanup.
        bucket.delete()
        keys.delete(key_pair)




        

