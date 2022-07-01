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
from twisted.internet.defer import setDebugging
setDebugging(True)

class ScanLineSpec():
    """
    Container for confguration of scanlines
    """
    def __init__(self, sx: int, sz: int, ex: int, ez: int, res: int, outfile):
        self.outfile = outfile
        self.sx = sx
        self.sz = sz
        self.ex = ex
        self.ez = ez
        self.resolution = res

class ScanLineControler(client.NocomControler):
    """
    Actual implemetation of scanline scanning
    """
    exhasted = False
    done_receving = False
    should_stop = True
    x = 0
    z = 0
    def __init__(self, spec):
        self.buffer = numpy.ndarray((spec.ex - spec.sx, spec.ez - spec.sz), dtype=numpy.uint8)
        self.buffer.fill(0)
        self.spec = spec
        self.x = spec.sx
        self.z = spec.sz
    def should_exit(self):
        return self.done_receving
    def on_exit(self):
        if self.should_stop:
            reactor.stop()
            self.should_stop = False
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
                self.done_receving = True
                Image.fromarray(self.buffer, "L").save(self.spec.outfile)
                print("Saving out, the program should now exit")
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

def errback(e):
    print("error - more info should follow")
    print(e)
    reactor.crash()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Use the nocom exploit to find loaded chunks')
    parser.add_argument('--token',metavar='token',type=str,help='Your minecraft token. go to https://kqzz.github.io/mc-bearer-token/ for instructions on how to get it. (lasts for 24h)', required=True)
    parser.add_argument('--resolution', type=int, help="How densly to check blocks. 128-256 is a good value, going under 16 is entirly pointless.", default=128)
    parser.add_argument('--outfile', type=str, help="file to save the result to", default="out.png")
    parser.add_argument('--port', type=int, help="Target server port", default=25565)
    parser.add_argument('host', type=str, help="Target server hostname")
    parser.add_argument('sx', type=int, help="Starting x cordinate (in terms of --resolution)", default=-30)
    parser.add_argument('sz', type=int, help="Starting z cordinate (in terms of --resolution)", default=-30)
    parser.add_argument('ex', type=int, help="End x cordinate (in terms of --resolution)", default=30)
    parser.add_argument('ez', type=int, help="End z cordinate (in terms of --resolution)", default=30)
    args = parser.parse_args()

    defer = twisted_main(args.token, args.sx, args.sz, args.ex, args.ez, args.resolution, args.host, args.port, args.outfile)
    defer.addErrback(errback)

    reactor.run()

@defer.inlineCallbacks
def twisted_main(token, sx, sz, ex, ez, res, server, port, outfile):
    print("logging in...")
    profile = yield auth.make_profile(token)
    print("initalizing...")
    factory = ScanLineFactory(profile, ScanLineSpec(sx, sz, ex, ez, res, outfile))
    print("connecting...")
    factory.connect(server, port)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


