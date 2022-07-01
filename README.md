# Block game radar

Find players using the nocom (no comment) exploit.

## Exploit explanation

Nocom exploits a [patch in paper](https://github.com/PaperMC/Paper/blob/ver/1.12.2/Spigot-Server-Patches/0196-Fix-block-break-desync.patch
), an optimized version of the minecraft server.

The patched server sends a BlockChange packet in response to a PlayerDigging packed, **if** the coordinates in the PlayerDigging packet is in a loaded chunk.

This is done even if the distance check (prevents digging far away blocks) *fails*. 

In effect, this allows a client to check if *any* chunk is loaded.

```java
if (d3 > 36.0D) {
	if (worldserver.isChunkLoaded(blockposition.getX() >> 4, blockposition.getZ() >> 4, true)) // Paper - Fix block break desync - Don't send for unloaded chunks
	       	this.sendPacket(new PacketPlayOutBlockChange(worldserver, blockposition)); // Paper - Fix block break desync
        return;
} else if (blockposition.getY() >= this.minecraftServer.getMaxBuildHeight()) {
```

# How do I use this?

To find loaded chunks, divide the starting and ending coordinates by the configured resolution (127 by default), and pass them into ``scanline.py``.

Full help info:

```
./scanline.py [-h] --token token [--resolution RESOLUTION] [--outfile OUTFILE] [--port PORT] host sx sz ex ez

Use the nocom exploit to find loaded chunks

positional arguments:
  host                  Target server hostname
  sx                    Starting x cordinate (in terms of --resolution)
  sz                    Starting z cordinate (in terms of --resolution)
  ex                    End x cordinate (in terms of --resolution)
  ez                    End z cordinate (in terms of --resolution)

options:
  -h, --help            show this help message and exit
  --token token         Your minecraft token. go to https://kqzz.github.io/mc-bearer-token/ for instructions on how to get it. (lasts for 24h)
  --resolution RESOLUTION
                        How densly to check blocks. 128-256 is a good value, going under 16 is entirly pointless.
  --outfile OUTFILE     file to save the result to
  --port PORT           Target server port
```

The loaded chunks will be shown as white pixels in out.png.
