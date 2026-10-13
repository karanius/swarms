"""Prompt existing libp2p peers to announce instead of waiting for their long mDNS interval."""
import socket
import struct
import time

name = b''.join(bytes([len(label)]) + label for label in (b'_p2p', b'_udp', b'local')) + b'\0'
query = struct.pack('!6H', 0, 0, 1, 0, 0, 0) + name + struct.pack('!HH', 12, 1)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as discovery:
    for _ in range(3):
        time.sleep(2)
        discovery.sendto(query, ('224.0.0.251', 5353))
