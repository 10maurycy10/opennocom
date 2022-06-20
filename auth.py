import json
from xmlrpc.client import ProtocolError
import requests
from twisted.python import failure
from twisted.internet import reactor
from quarry.types.uuid import UUID
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.net import auth, crypto
from twisted.internet import reactor

# Microsoft authenticated client
# Based on example proxy published by Jerrylum in https://github.com/barneygale/quarry/issues/135

class AuthClientProtocol(SpawningClientProtocol):
    def packet_login_encryption_request(self, buff):
        print("Got auth request")
        p_server_id = buff.unpack_string()

        # 1.7.x
        if self.protocol_version <= 5:
            def unpack_array(b): return b.read(b.unpack('h'))
        # 1.8.x
        else:
            def unpack_array(b): return b.read(b.unpack_varint(max_bits=16))

        p_public_key = unpack_array(buff)
        p_verify_token = unpack_array(buff)

        if not self.factory.profile.online:
            raise ProtocolError("Can't log into online-mode server while using"
                                " offline profile")

        self.shared_secret = crypto.make_shared_secret()
        self.public_key = crypto.import_public_key(p_public_key)
        self.verify_token = p_verify_token

        # make digest
        digest = crypto.make_digest(
            p_server_id.encode('ascii'),
            self.shared_secret,
            p_public_key)

        # do auth
        # deferred = self.factory.profile.join(digest)
        # deferred.addCallbacks(self.auth_ok, self.auth_failed)

        url = "https://sessionserver.mojang.com/session/minecraft/join"

        payload = json.dumps({
            "accessToken": self.factory.profile.access_token,
            "selectedProfile": self.factory.profile.uuid.to_hex(False),
            "serverId": digest
        })
        headers = {
            'Content-Type': 'application/json'
        }

        r = requests.request(
            "POST", "https://sessionserver.mojang.com/session/minecraft/join", headers=headers, data=payload)

        if r.status_code == 204:
            print("auth done")
            self.auth_ok(r.text)
        else:
            self.auth_failed(failure.Failure(
                auth.AuthException('unverified', 'unverified username')))

def make_profile(accessToken):
    """
    Support online mode
    """
    url = "https://api.minecraftservices.com/minecraft/profile"
    headers = {'Authorization': 'Bearer ' + accessToken}
    response = requests.request("GET", url, headers=headers)
    result = response.json()
    myUuid = UUID.from_hex(result['id'])
    myUsername = result['name']
    return auth.Profile('(skip)', accessToken, myUsername, myUuid)
