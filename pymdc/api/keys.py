from pymdc.rest import REST
from pymdc.keypair import ECDSA

# A list of ECDSA objects for a user account.
# Requires HTTP basic auth.
class Keys():
    def __init__(self, user):
        self.user = user
        self.key_pairs = []

    def list(self, callback=None):
        resource = "/keys"
        ret = REST(
            "GET",
            resource,
            callback=callback,
            auth=self.user
        )

        return ret

    # Hex ECDSA pub key.
    def create(self, key_pair=None, callback=None):
        key_pair = key_pair or ECDSA()
        if key_pair not in self.key_pairs:
            self.key_pairs.append(key_pair)

        params = {
            "key": key_pair.get_public_key("hex")
        }

        ret = REST(
            "POST",
            "/keys",
            params,
            callback=callback,
            auth=self.user
        )

        return ret

    def delete(self, key_pair, callback=None):
        if key_pair in self.key_pairs:
            self.key_pairs.remove(key_pair)

        resource = "/keys/%s" % key_pair.get_public_key("hex")
        ret = REST(
            "DELETE",
            resource,
            callback=callback,
            auth=self.user
        )

        return ret
