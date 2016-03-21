from pymdc.rest import REST
import hashlib
import os

class Users():
    def __init__(self, username, password=None):
        rand = lambda: hashlib.sha256(os.urandom(15)).hexdigest()
        self.username = username
        self.password = password or rand()

    def password_hash(self):
        return hashlib.sha256(self.password).hexdigest()
        
    def register(self, callback=None):
        password = self.password_hash()
        params = {
            "email": self.username,
            "password": password
        }

        return REST("POST", "/users", params, callback=callback)

    def activate(self, token, callback=None):
        resource = "/activations/%s" % token

        return REST("GET", resource, callback=callback)
