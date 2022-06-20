import auth
from twisted.internet import reactor,defer
from quarry.net.client import ClientFactory, SpawningClientProtocol
import json
import random
import logging

class NocomClientProtocol(auth.AuthClientProtocol):
    # Log all packets sent by server
    seq = 0
    def packet_unhandled(self, buff, name):
        #print(name)
        buff.discard()
    def packet_block_change(self, buff):
        """
        Handles block_change packets sent by the paper server if the queryed chuck us loaded
        """
        pos = buff.unpack_position()
        block = buff.unpack_varint()
        logging.info(f"update {pos}")
    def query_next(self):
        """
        calles query_block if the mode is play
        """
        if self.pos_look[1] != 0: 
            if ( self.protocol_mode == 'play' ): 
                self.query_block(int(self.pos_look[0]), int(self.pos_look[1]-2), int(self.pos_look[2]))
    def query_block(self, x,y,z):
        """
        Sends a player digging packet with given (block) cordinates.
        """
        self.send_packet(
                "player_digging", 
                self.buff_type.pack_varint(2), # start digging
                self.buff_type.pack_position(x,y,z), # Position
                self.buff_type.pack("b",1), # face -Y
                #self.buff_type.pack_varint(self.seq) # sequence number
        )
        self.seq += 1
        logging.info(f"breaking ({x}, {y}, {z})")
    def setup(self):
        self.ticker.add_loop(10, self.query_next)
        pass

class NocomClientFactory(ClientFactory):
    protocol = NocomClientProtocol

config = json.loads(open("config.json").read())

def get_chunk_cords():
    rand()

@defer.inlineCallbacks
def main(args):
    print("logging in...")
    profile = yield auth.make_profile(config["minecraft-token"])
    factory = NocomClientFactory(profile)
    print("connecting...")
    #factory = factory.connect('w.viw.se', 25569)
    #factory = factory.connect('constantiam.net', 25565)
    factory = factory.connect('158.101.134.14', 25565)
    print("connected!")

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
    reactor.run()
