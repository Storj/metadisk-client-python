from bitcoin.core import x, Hash160
from bitcoin.core.key import CPubKey
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from collections import OrderedDict
import ecdsa.util
import base64
import binascii
import re
import hashlib
import time
import json
import urllib
import os

"""
Takes an unknown string and returns bytes.
* If the string is a hex string it will be decoded.
* If the string is base64 encoded it will be decoded.
"""
def auto_bytes(s):
    #None.
    if s == None:
        return s

    #Already bytes.
    if type(s) == type(b""):
        return s

    #Hex string.
    if re.match("^[#][0-9a-fA-F]+$", s) != None and not ((len(s) - 1) % 2):
        return binascii.unhexlify(s[1:])

    #Base64 string.
    if re.match("^[a-zA-Z0-9+=/]+$", s) != None:
        try:
            return base64.b64decode(s)
        except:
            pass

    return s.encode("ascii")

def pow_mod(x, y, z):
    "Calculate (x ** y) % z efficiently."
    number = 1
    while y:
        if y & 1:
            number = number * x % z
        y >>= 1
        x = x * x % z
    return number

class ECDSA:
    def __init__(self, public_key=None, private_key=None):
        self.id = 0
        if public_key is not None:
            public_key = "#" + public_key

        if private_key is not None:
            private_key = "#" + private_key

        self.public_key = auto_bytes(public_key)
        self.private_key = private_key
        self.addr_version = None
        self.use_compression = 1
        if private_key == "":
            private_key = None

        #Generate key pairs.
        if self.public_key == None and private_key == None:
            self.sign_key = SigningKey.generate(curve=SECP256k1)
            self.verify_key = self.sign_key.get_verifying_key()
            self.private_key = self.sign_key.to_string()
            self.public_key = self.verify_key.to_string()
            return

        #Init public key.
        self.old_verify_str = None
        if self.public_key != None:
            self.public_key = self.parse_public_key(self.public_key)
            self.verify_key = VerifyingKey.from_string(self.public_key, SECP256k1)
            self.sign_key = None
            self.old_verify_str = self.verify_key.to_string()

        #Init private key.
        if self.private_key != None:
            #Construct keys from private key.
            self.private_key = self.parse_private_key(private_key)
            self.sign_key = SigningKey.from_string(self.private_key, SECP256k1) 
            self.verify_key = self.sign_key.get_verifying_key()

            #Check private key corrosponds to public key.
            if self.old_verify_str != None:
                if self.old_verify_str != self.verify_key.to_string():
                    raise Exception("Private key doesn't corrospond to stored public key.")

    #Input = b58check || b64 || hex private key
    #Output = binary ECDSA private key.
    def parse_private_key(self, private_key):
        if type(private_key) == str:
            #Base58 string.
            if re.match("^[!][" + b58 + "]+$", private_key) != None:
                try:
                    priv, version, compressed, checksum = PrivateKey().wif_to_private(private_key[1:])
                    self.addr_version = version
                    return priv
                except:
                    pass

        return auto_bytes(private_key)

    #Input = b64encoded public key.
    #Output = ECDSA-style (non-prefixed) decompressed public key.
    def parse_public_key(self, public_key):
        public_key = auto_bytes(public_key)

        #Key is valid compressed key.
        if len(public_key) == 64:
            return public_key

        #Key is valid but contains prefix.
        if len(public_key) == 65:
            return public_key[1:]

        #Invalid compressed key.
        if len(public_key) == 32:
            raise Exception("Prefix byte for compressed pub key not known.")
            #public_key = bytes([3]) + public_key

        #Decompress the key.
        if len(public_key) == 33:
            return self.decompress_public_key(public_key)[1:]

        return public_key            

    #Input: str, str
    #Output: str b64 encoded sig
    def sign(self, msg, private_key=None):
        if private_key == None:
            sign_key = self.sign_key
        else:
            private_key = self.parse_private_key(private_key)
            sign_key = SigningKey.from_string(private_key, SECP256k1)

        if sign_key == None:
            raise Exception("Private key for ECDSA keypair not known.")

        if type(msg) == str:
            msg = msg.encode("ascii")

        return binascii.hexlify(sign_key.sign(msg, sigencode=ecdsa.util.sigencode_der, hashfunc=hashlib.sha256)).decode("utf-8")

    #Input: b64 encoded pub key, b64 encoded sig, str msg
    #Output: boolean
    def valid_signature(self, signature, msg, public_key=None):
        try:
            if type(msg) == str:
                msg = msg.encode("ascii")

            #Parse public key.
            if public_key == None:
                public_key = self.public_key
            else:
                public_key = self.parse_public_key(public_key)

            signature = auto_bytes(signature)
            msg = auto_bytes(msg)
            verify_key = VerifyingKey.from_string(public_key, SECP256k1)
            return verify_key.verify(signature, msg)
        except Exception as e:
            print(e)
            return 0

    #Input: compressed prefixed pub key bytes
    #Output: decompressed prefixed pub key bytes
    def decompress_public_key(self, public_key):
        #https://bitcointalk.org/index.php?topic=644919.0
        public_key = auto_bytes(public_key)
        public_key = binascii.hexlify(public_key)
        public_key = public_key.decode("utf-8")

        p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
        y_parity = int(public_key[:2]) - 2
        x = int(public_key[2:], 16)

        a = (pow_mod(x, 3, p) + 7) % p
        y = pow_mod(a, (p+1)//4, p)
        if y % 2 != y_parity:
            y = -y % p
        x = "{0:0{1}x}".format(x, 64)
        y = "{0:0{1}x}".format(y, 64)

        ret = "04" + x + y

        return binascii.unhexlify(ret)

    #Input: decompressed prefixed pub key bytes
    #Output: decompressed prefixed pub key bytes
    def compress_public_key(self, public_key):
        #https://bitcointalk.org/index.php?topic=644919.0
        public_key = auto_bytes(public_key)
        public_key = binascii.hexlify(public_key).decode("utf-8")

        #Is there a prefix byte?
        if len(public_key) == 128:
            offset = 0
        else:
            offset = 2

        #Extract X from X, Y public key.
        x = int(public_key[offset:64 + offset], 16)
        y = int(public_key[65 + offset:], 16)

        if y % 2:
            prefix = "03"
        else:
            prefix = "02"

        #Return compressed public key.
        ret = prefix + "{0:0{1}x}".format(x, 64)
        return binascii.unhexlify(ret)

    #Input: prefixed pub key bytes
    #Output: boolean
    def validate_public_key(self, public_key):
        public_key = auto_bytes(public_key)
        public_key = binascii.hexlify(public_key).decode("utf-8")
        prefix = public_key[0:2]
        if prefix == "04":
            is_compressed = 0
        else:
            is_compressed = 1

        return is_compressed

    #Returns a Bitcoin style public_key (prefixed)
    def get_public_key(self, f="hex", public_key=None):
        if public_key == None:
            public_key = self.public_key

        #O4 = uncompressed.
        public_key_hex = "04" + binascii.hexlify(public_key).decode("utf-8")
        if self.use_compression:
            public_key = binascii.unhexlify(public_key_hex)
            public_key = self.compress_public_key(public_key)
            public_key_hex = binascii.hexlify(public_key).decode("utf-8")
        else:
            public_key = binascii.unhexlify(public_key_hex)

        cpub = CPubKey(x(public_key_hex))

        if f == "bin":
            return public_key

        elif f == "hex":
            return public_key_hex.decode("utf-8")

        elif f == "cpub":
            return cpub

        elif f == "hash":
            return Hash160(cpub)

        else:
            return base64.b64encode(public_key).decode("utf-8")

    def get_private_key(self, f="hex"):
        if f == "bin":
            return self.private_key

        elif f == "hex":
            return binascii.hexlify(self.private_key).decode("utf-8")

        elif f == "wif":
            if self.addr_version == None:
                raise Exception("Addr version for priv key not known.")
            priv, version, compressed, checksum = PrivateKey().private_to_wif(self.private_key, self.addr_version, self.use_compression)
            return priv

        else:
            return base64.b64encode(self.private_key).decode("utf-8")
