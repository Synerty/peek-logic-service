import hashlib
import json
import subprocess
from base64 import b64decode, b64encode

from Crypto.Cipher import AES


def authKey() -> str:
    def makeFingerPrint(val):
        m = hashlib.sha1()
        m.update(val.replace(b' ', b'').strip())
        isgood = lambda c : chr(c).isalnum() and c not in b'0O'
        hexVal = ''.join([chr(c) for c in b64encode(m.digest()).upper() if isgood(c)])
        return "%s-%s-%s" % (hexVal[0:5], hexVal[5:9], hexVal[9:14])

    args = b64decode("c3VkbyAvdXNyL3NiaW4vZG1pZGVjb2RlIC10IDEgfCBncmVwIFNlcmlhbCB8"
                     "IGN1dCAtZjIgLWQ6O3N1ZG8gL3Vzci9zYmluL2RtaWRlY29kZSAtdCA0IHwg"
                     "Z3JlcCBJRCB8IGN1dCAtZjIgLWQ6IHwgaGVhZCAtMTtjYXQgL3N5cy9jbGFz"
                     "cy9uZXQvZXRoPy9hZGRyZXNzIHwgaGVhZCAtMTs=")
    popen = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout = popen.stdout.read()
    stderr = popen.stderr.read()
    stderr = b'\n'.join([l for l in stderr.splitlines() if not b'resolve host' in l])

    if b'sudo: ' in stderr:
        print(stderr)
        return "Could not generate Server ID"

    return makeFingerPrint(stdout)

class KeyInvalidException(Exception):
    pass



def loadCapabilities(destObj, data):
    destObj._capabilities = None
    if not data:
        return

    key = authKey()
    if ' ' in key:
        return None

    data = data.replace('\r', '').replace('\n', '').strip()

    synKey = 'fM66hbfd15zkLFso'
    obj = AES.new(key + synKey, AES.MODE_CBC, synKey)
    capabilities = obj.decrypt(b64decode(data)).strip().decode()
    if not (capabilities[0] == '{' and capabilities[-1] == '}'):
        return None

    capabilities = json.loads(capabilities)
    destObj._capabilities = capabilities
