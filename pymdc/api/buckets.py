from pymdc.rest import REST
from pymdc.api.files import Files

# A list of bucket objects for a user account.
class Buckets():
    def __init__(self, key_pair):
        self.key_pair = key_pair

    def create(self, name, storage, transfer, key_pairs, callback=None):
        # Get pub keys.
        pub_keys = []
        for key_pair in key_pairs:
            pub_keys.append(key_pair.get_public_key("hex"))

        params = {
            "name": name,
            "storage": int(storage),
            "transfer": int(transfer),
            "pubkeys": pub_keys
        }

        ret = REST(
            "POST",
            "/buckets",
            params,
            callback=callback,
            auth=self.key_pair
        )

        return ret

    def list(self, callback=None):
        resource = "/buckets"
        ret = REST(
            "GET",
            resource,
            callback=callback,
            auth=self.key_pair
        )

        return ret

# A bucket is also an object that can store + download files.
class Bucket():
    def __init__(self, bucket_id, key_pair):
        self.bucket_id = bucket_id
        self.key_pair = key_pair
        self.files = Files(self.bucket_id, self.key_pair)
    
    def list(self, callback=None):
        resource = "/buckets/%s" % self.bucket_id
        ret = REST(
            "GET",
            resource,
            callback=callback,
            auth=self.key_pair
        )

        return ret

    def delete(self, callback=None):
        resource = "/buckets/%s" % self.bucket_id
        ret = REST(
            "DELETE",
            resource,
            callback=callback,
            auth=self.key_pair
        )

        return ret

    def patch(self, params, callback=None):
        resource = "/buckets/%s" % self.bucket_id
        ret = REST(
            "PATCH",
            resource,
            params=params,
            callback=callback,
            auth=self.key_pair
        )

        return ret
