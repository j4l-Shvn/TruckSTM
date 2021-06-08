import time
import argparse


def ingest_logs(logfile: str):
    with open(logfile, 'r') as fh:
        logs = fh.read()
        logs = logs.split('\n')
        for i, line in enumerate(logs):
            if len(line) > 0:
                tmp = line.split(' ')
                logs[i] = (bytes.fromhex(tmp[0]), float(tmp[1]))
            else:
                logs.pop(i)
    return logs


def init_rp1210():
    print("Looking for DPA 5")
    speed = "Auto"
    dll_name = "DGDPA5MA"
    RP1210 = RP1210Class(dll_name)

    for deviceID in range(1, 6):
        client_id = RP1210.get_client_id("J1939", deviceID, "{}".format(speed))
        if client_id is not None:
            print("Found device")
            break
    else:
        print("Failed to find compatible device. Ensure DPA 5 is connected and drivers are installed.")
        exit()
    return RP1210, client_id


def init_socketcan():
    return can.interface.Bus(channel='vcan0', bustype='socketcan')


class CanReplay(object):
    def __init__(self, logs: list, socketcan: bool):
        self.logfile = logs
        self.use_socketcan = socketcan
        self.sock = None
        self.rp_client = None
        self.rp_client_id = None
        if self.use_socketcan:
            self.sock = init_socketcan()
        else:
            self.rp_client, self.rp_client_id = init_rp1210()

    def send(self, rp1210_data):
        if self.sock is not None and self.use_socketcan:
            # Filter out DPA 5 stuff
            if int.from_bytes(rp1210_data[:2], 'little') == 65265:
                arb_id = 0x18FEF100  # PGN 65265
            else:
                arb_id = 0x18FDCC00  # PGN 64972
            data = rp1210_data[-8:]
            self.sock.send(can.Message(arbitration_id=arb_id, data=data, is_extended_id=True))
        elif self.rp_client is not None:
            self.rp_client.send_message(self.rp_client_id, rp1210_data[:])
        else:
            print("Failed to initialize either a socket can sock or RP1210 client. Exiting")
            exit()

    def play_log(self):
        start = time.time()
        width = 40
        for i, (msg, delta) in enumerate(self.logfile):
            progress = '=' * int(width * (i / len(self.logfile)))
            progress = '[' + progress + (' ' * (width - len(progress))) + ']'
            print(progress, flush=True, end='\r')
            # wait for time delta
            while time.time() < (start + delta):
                pass
            self.send(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN log replay script")
    parser.add_argument("filename", help="The name of the file you wish to replay")
    parser.add_argument("-r", "--repeat", action='store_true', default=False, help="repeat log file")
    parser.add_argument("--socketcan", action='store_true', default=False,
                        help="Send log files over virtual can interface")
    args = parser.parse_args()
    if args.socketcan:
        import can
    else:
        from RP1210.RP1210 import *

    replayer = CanReplay(ingest_logs(args.filename), args.socketcan)

    if args.repeat:
        try:
            print("Sending logs on repeat")
            while True:
                replayer.play_log()
        except KeyboardInterrupt:
            print()
            exit()
    else:
        print("Sending logs...")
        replayer.play_log()
        print("\nLogs sent")
