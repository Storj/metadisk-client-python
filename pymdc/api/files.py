from pymdc.rest import REST
import os

class Files():
    def __init__(self, bucket_id, key_pair):
        self.bucket_id = bucket_id
        self.key_pair = key_pair

    def list(self, callback=None):
        resource = "/buckets/%s/files" % self.bucket_id
        ret = REST(
            "GET",
            resource,
            callback=callback,
            auth=self.key_pair
        )

        return ret

    def token(self, operation, callback=None):
        params = {
            "id": self.bucket_id,
            "operation": operation
        }

        ret = REST(
            "POST",
            "/buckets/%s/tokens" % self.bucket_id,
            params,
            callback=callback,
            auth=self.key_pair
        )

        return ret

    def upload(self, path, token, callback=None):
        file_size = os.path.getsize(path)
        params = {
            "id": self.bucket_id,
            "file": open(path, mode="rb")
        }

        headers = {
            "x-token": token,
            "x-filesize": file_size
        }

        ret = REST(
            "PUT",
            "/buckets/%s/files" % self.bucket_id,
            params,
            headers=headers,
            callback=callback,
            auth=self.key_pair
        )

        return ret


    def download(self, file_hash, token, callback=None):
        resource = "/buckets/%s/files/%s" % (
            self.bucket_id,
            file_hash
        )

        headers = {
            "x-token": token
        }

        ret = REST(
            "GET",
            resource,
            headers=headers,
            callback=callback,
            auth=self.key_pair
        )

        return ret
