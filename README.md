# metadisk-client-python

This library lets you talk with the Metadisk API from Python. It offers both asynchronous callback-based programming and synchronous (blocking style.)

### To do:
* Finish download code (sorry - will be done soon.)
* Make library more robust with timeout errors + connection interruptions
* Write unit tests
* Test python 2 / 3 -- add this to Travis too

### 1. Register an account

To start using the API you first need to register a new user. This will be sent over HTTPS so don't worry about security.

```python
import pymdc

user = pymdc.api.Users("your_email@some_domain.com", "your password")
user.register()
```

```javascript
{
u'id': u'new_user@coinbend.com',
u'activated': False,
u'email': u'new_user@coinbend.com',
u'created': u'2016-03-20T16:55:44.321Z'
}
```

The user account is now created but it needs to be activated. The activation link can be found in your email. The link looks something like this: https://api.metadisk.org/activations/0aa6b301d0aa01f3e3580d0ab118e7257343325a41de20fb158dbbc7fd1225a5

Note the hex at the end -- this is the activation key. You can click the link directly or you can programmatically activate the account using the token.

```python
user.activate("0aa6b301d0aa01f3e3580d0ab118e7257343325a41de20fb158dbbc7fd1225a5")
```

```javascript
{
u'id': u'new_user@coinbend.com',
u'activated': True,
u'email': u'new_user@coinbend.com',
u'created': u'2016-03-20T16:55:44.321Z'
}
```

### 2. Add an ECDSA key pair to your account

Now that you have an account its time to create an ECDSA key pair. The key pair will be associated with your account and used to sign all future requests against that account.

```python
key_pair = pymdc.keypair.ECDSA()
keys = pymdc.api.keys.Keys(user)
keys.create(key_pair)
```

```javascript
{
u'user': u'new_user@coinbend.com',
u'key': u'03a31fa025888eef19833b204aead95192bc4b52f8447a8c8341920e1d9a437108',
u'id': u'03a31fa025888eef19833b204aead95192bc4b52f8447a8c8341920e1d9a437108'
}
```

You can view the public keys associated with your account by listing them.

```python
keys.list()
```

```javascript
[{
u'user': u'new_user@coinbend.com',
u'key': u'03a31fa025888eef19833b204aead95192bc4b52f8447a8c8341920e1d9a437108',
u'id': u'03a31fa025888eef19833b204aead95192bc4b52f8447a8c8341920e1d9a437108'
}]
```

Public keys can also be deleted.

```python
keys.delete(key_pair)
```

Btw, you can save your ECDSA key pair easily like this:

```python
pub_key = key_pair.get_public_key()
priv_key = key_pair.get_private_key()
key_pair = pymdc.keypair.ECDSA(pub_key, priv_key)
```

### 3. Create a bucket to store files.

Now its time to create a bucket to store your files. Buckets are logical places to store related files and they define how much virtual space you can use (storage) and how much bandwidth can be consumed by downloads (transfer.)

```python
buckets = pymdc.api.buckets.Buckets(key_pair)
storage = 10  # GB
transfer = 10  # GB
bucket_id = buckets.create("My cat pictures", storage, transfer, [key_pair])
```

```javascript
{
u'status': u'Active',
u'name': u'My cat pictures',
u'created': u'2016-03-20T17:13:42.590Z',
u'transfer': 10,
u'storage': 10,
u'user': u'new_user@coinbend.com',
u'pubkeys': [u'03a49c80327f1726ea4cf3050169f36087b0c1232c765421428c704cedd68886ec'],
u'id': u'56eeda4656bf7b950faace4a'
}
```

You can list all buckets from the account by doing this.

```python
buckets.list()
```

```javascript
[{
u'status': u'Active',
u'name': u'My cat pictures',
u'created': u'2016-03-20T17:13:42.590Z',
u'transfer': 10,
u'storage': 10,
u'user': u'new_user@coinbend.com',
u'pubkeys': [u'03a49c80327f1726ea4cf3050169f36087b0c1232c765421428c704cedd68886ec'],
u'id': u'56eeda4656bf7b950faace4a'
}]
```

Now that you have a bucket its easy to list, update, and delete it.

```python
bucket = pymdc.api.buckets.Bucket(bucket_id=u"56eeda4656bf7b950faace4a", key_pair=key_pair)
```

Here's how to show meta data about a bucket.

```python
bucket.list()
```

```javascript
{
u'status': u'Active',
u'name': u'My files',
u'created': u'2016-03-20T17:12:50.739Z',
u'transfer': 10,
u'storage': 10,
u'user': u'new_user@coinbend.com',
u'pubkeys': [u'03a49c80327f1726ea4cf3050169f36087b0c1232c765421428c704cedd68886ec'],
u'id': u'56eeda1256bf7b950faace49'
}
```

It's also easy to delete buckets.

```python
bucket.delete()
```

### 4. Upload something to the bucket.

Now that you understand how to create a bucket it's time to try upload something, but first you need to create a PUSH token.

```python
bucket.files.token("PUSH")
```

```javascript
{
u'operation': u'PUSH',
u'expires': u'2016-03-20T17:30:55.840Z',
u'bucket': u'56eedc7056bf7b950faace4b',
u'token': u'56b88113f5ecd4f56fa01336a06399e1586dee75069f963c522a9b38aba15c57',
u'id': u'56b88113f5ecd4f56fa01336a06399e1586dee75069f963c522a9b38aba15c57'
}
```

Now lets upload a file for the first time.

```python
path = r"""C:\Users\Matthew\Desktop\san_francisco.jpg"""
token = u'56b88113f5ecd4f56fa01336a06399e1586dee75069f963c522a9b38aba15c57'
bucket.files.upload(path, token)
```

```javascript
{
u'mimetype': u'image/jpeg',
u'hash': u'5579439f51de8508db790f7fe1212d601afb5c51',
u'size': 68155,
u'bucket': u'56eee24d56bf7b950faace69',
u'filename': u'san_francisco.jpg'
}
```

You can list meta data about the files in that bucket like this.

```python
bucket.files.list()
```

```javascript
[{
u'mimetype': u'image/jpeg',
u'hash': u'5579439f51de8508db790f7fe1212d601afb5c51',
u'size': 68155,
u'bucket': u'56eee24d56bf7b950faace69',
u'filename': u'san_francisco.jpg'
}]
```

### 5. Download something from the bucket.

Not yet implemented. Sorry about that.

### Bonus section - async callbacks

All functions accept a callback parameter that defines the name of the function to receive the result. The result for that function is a dictionary representing the JSON returned from that call. Example.

```python

def callback(result):
    print("In callback.")
    print(result)
    
user.register(callback=callback)

>>> In callback
{u'error': u'Email is already registered'}
```

If you don't specify a callback for an API call then that call will block the main program and you will get a dictionary for the JSON result as the return value instead.

Fin.
    
