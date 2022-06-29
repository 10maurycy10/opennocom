"""
A very simple search pattern for nocom
"""
from quarry.net.client import ClientFactory

import client
import auth
import json
import logging
from twisted.internet import reactor,defer,stdio
import numpy
from PIL import Image

class ScanLineSpec():
    """
    Container for confguration of scanlines
    """
    resolution = 16*2
    def __init__(self, sx: int, sz: int, ex: int, ez: int):
        self.sx = sx
        self.sz = sz
        self.ex = ex
        self.ez = ez

class ScanLineControler(client.NocomControler):
    """
    Actual implemetation of scanline scanning
    """
    exhasted = False
    done_receving = False
    x = 0
    z = 0
    def __init__(self, spec):
        self.buffer = numpy.ndarray((spec.ex - spec.sx, spec.ez - spec.sz), dtype=numpy.uint8)
        self.buffer.fill(0)
        self.spec = spec
        self.x = spec.sx
        self.z = spec.sz
    def should_exit(self):
        self.done_receving
    def next_location(self):
        res = self.spec.resolution
        if self.exhasted: # if search space is finished, return nothing
            return None
        loc = [self.x * res, 1, self.z * res]
        if self.x >= self.spec.ex:
            self.x = self.spec.sx
            print(f"Scanning z={self.z*res}. [{self.z}]")
            if self.z >= self.spec.ez: # If done on the z axis, stop scanning
                self.exhasted = True
                Image.fromarray(self.buffer, "L").save("out_new.png")
                return None
            self.z += 1
        else:
            self.x += 1
        return loc
    def on_update(self, x, y, z, block):
        res = self.spec.resolution
        chunkpos = [x//res, z//res]
        self.buffer[chunkpos[0] - self.spec.sx][chunkpos[1] - self.spec.sz] = 255
        print(f"{x} {x} {y} [{chunkpos[0]} {chunkpos[0]}]")

class ScanLineFactory(ClientFactory):
    protocol = client.ControledNocomClientProtocol
    def __init__(self, profile, spec: ScanLineSpec):
        self.profile = profile
        self.spec = spec
    def buildProtocol(self, addr):
        nocom = super(ScanLineFactory, self).buildProtocol(addr)
        controler = ScanLineControler(self.spec)
        nocom.controler = controler
        return nocom

config = json.loads(open("config.json").read())

@defer.inlineCallbacks
def main(args):
    print("logging in...")
    profile = yield auth.make_profile(config["minecraft-token"])
    print("makeing instance")
    factory = ScanLineFactory(profile, ScanLineSpec(-30, -30, 30, 30))
    print("connecting")
    factory.connect('85.159.210.228', 25565)
    #factory.connect('localhost', 25565)
    print("connected")

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
    reactor.run()


