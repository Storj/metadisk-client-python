import pymdc.unirest as unirest
import time
import json
import urllib
from collections import OrderedDict
from pymdc.keypair import ECDSA

############################################
# Begin monkey patch for unirest.delete.

def patched_delete(url, **kwargs):
    params = unirest.get_parameters(kwargs)
    if len(params) > 0:
        if url.find("?") == -1:
            url += "?"
        else:
            url += "&"
        url += unirest.utils.dict2query(dict((k, v) for k, v in params.items() if v is not None))  # Removing None values/encode unicode objects

    return unirest.__dorequest("DELETE", url, {}, kwargs.get(unirest.HEADERS_KEY, {}), kwargs.get(unirest.AUTH_KEY, None), kwargs.get(unirest.CALLBACK_KEY, None))

unirest.delete = patched_delete

# End monkey patch for unirest.delete.
############################################

def REST(method, resource, params={}, auth=(), headers={}, callback=None):
    # API location.
    endpoint = "https://api.metadisk.org"

    # ASYNC request handlers.
    method_handlers = {
        "GET": unirest.get,
        "POST": unirest.post,
        "DELETE": unirest.delete,
        "PATCH": unirest.patch,
        "PUT": unirest.put
    }

    # Find handler for HTTP method.
    handler = method_handlers[method]

    # Callback wrapper.
    if callback is not None:
        wrapper = lambda response: callback(response.body)
    else:
        wrapper = None

    # Add nonce to params.
    # Should prob be UUID for future versions.
    params["__nonce"] = time.time()
    if method is not "PUT":
        content = json.dumps(params, separators=(',', ':'))
    else:
        content = params

    # Build content.
    if method in ["GET", "DELETE"]:
        # For GET and DELETE -- the content to push gets
        # added to the URL as a query string instead of as
        # a post body. This tells the request library to
        # use the same order as the payload we sign later on.
        content = payload = json.loads(content, object_pairs_hook=OrderedDict)
        payload = urllib.urlencode(payload)

    # Set authentication (use basic or not.)
    if hasattr(auth, 'password_hash'):
        if hasattr(auth.password_hash, '__call__'):
            basic_auth = (auth.username, auth.password_hash())
        else:
            basic_auth = ()
    else:
        basic_auth = ()

    # Set authentication (ECDSA sig)
    url = endpoint + resource
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    if isinstance(auth, ECDSA) and "x-token" not in headers:
        # Build contract.
        if method not in ["GET", "DELETE"]:
            payload = json.dumps(params, separators=(',', ':'))
        contract = "\n".join([
            method,
            resource,
            payload
        ])

        # print(contract)

        # Sign contract.
        sig = auth.sign(contract)

        # Set headers.
        headers["x-pubkey"] = auth.get_public_key("hex")
        headers["x-signature"] = sig

    # print(basic_auth)
    # print(params)
    # print(url)
    # print(method)
    # print(content)
    # print(headers)
    # print(handler)

    # Convert unicode to bytes.
    request_info = []
    for obj in [headers, content, basic_auth]:
        if type(obj) == dict:
            for key, value in obj.items():
                if type(key) == type(u""):
                    del obj[key]
                    key = key.encode("ascii")

                if type(value) == type(u""):
                    obj[key] = value.encode("ascii")
        else:
            if type(obj) == type(u""):
                obj = obj.encode("ascii")

        request_info.append(obj)

    headers, content, basic_auth = request_info

    # Make call.
    ret = handler(
        url,
        headers=headers,
        params=content,
        callback=wrapper,
        auth=basic_auth
    )

    # Async = get response object
    # Sync = get HTTP response
    if callback is None:
        # Valid JSON / dict response
        if hasattr(ret, 'body'):
            return ret.body

    return ret
