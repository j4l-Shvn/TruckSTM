# Local imports
import binascii, sys, lib.file_io as fi

# The pgn_h, spn + mask map
pgn_spn_map = {}


def process(val):  # for this module, val is the message
    try:
        masks = pgn_spn_map[val['ID'][2:]]
    except:
        return None
    out = []
    for entry in masks:
        bin_val = (val['Data'] & entry[1]) >> entry[4]
        result = None
        if (entry[2] == "ASCII"):
            result = ""
            hex_result = hex(bin_val)[2:]
            if len(hex_result) % 2 != 0:
                hex_result = '0' + hex_result
            for i in range(len(hex_result), 1, -2):
                result = result + binascii.unhexlify(hex_result[i - 2:i])
        elif (entry[2] == "Binary" or entry[2] == "bit-mapped"):
            result = str(bin(bin_val))[2:]
        else:
            result = bin_val * entry[2] + entry[3]

        out.append((entry[0], result))

    return out


def start_up(args):
    global pgn_spn_map
    pgn_spn_map = args['startup']


def communicate(in_q, out_q, args):  # args is a dictionary of whatever this module needs
    start_up(args)
    import lib.process as proc
    proc.io(in_q, out_q, process, "J1939_Interpreter")
