import json
from lib.input_checker import validate_state_defs


def state_def_interpreter(inp_file):

    with open(inp_file) as def_file:
        states_from_file = json.load(def_file)

    validate_state_defs(states_from_file)

    # General
    identifier = 0

    # For the Interpreter
    pgn_spn_map = {}

    # For the state-indexer
    parameter_state_map = {}
    state_parameter_map = {}

    # For the state-visulazer
    state_visualizer_map = {}

    for states in states_from_file:
        state_switch_dict = {}
        state_name = (states['name'], identifier)
        for def_dict in states['definition']:
            # first for the ID filter mask
            pgn_h = "{:04X}".format(def_dict['parameter']['pgn'])
            da_h = "{:02X}".format(def_dict['parameter']['da'])
            sa_h = "{:02X}".format(def_dict['parameter']['sa'])
            if int(pgn_h[:2], 16) < 240:  # if pf < 240, mask da into pgn
                pgn_h = pgn_h[:2] + da_h
            pgn_h = pgn_h + sa_h

            # Next prepare the pgn spn map
            tup = pgn_spn_map.get(pgn_h, (def_dict['parameter']['pgn'], def_dict['parameter']['da'], def_dict['parameter']['sa'], set()))
            tup[3].add(def_dict['parameter']['spn'])
            pgn_spn_map[pgn_h] = tup

            # Next for all the stuff to he sent to the state-indexer
            # For state_parameter_map
            state_switch_dict[(def_dict['parameter']['pgn'], def_dict['parameter']['da'], def_dict['parameter']['sa'], def_dict['parameter']['spn'])] = 0
            # For parameter_state_map
            psmap = parameter_state_map.get((def_dict['parameter']['pgn'], def_dict['parameter']['da'], def_dict['parameter']['sa'], def_dict['parameter']['spn']),
                                            ({}, {}))
            psmap[0][state_name] = 0
            # For parameter_state_map values
            for item in def_dict['pinstset']:
                if isinstance(item, list):
                    item = tuple(item)
                else:
                    item = (item,)
                imap = psmap[1].get(item, set())
                imap.add(state_name)
                psmap[1][item] = imap

            parameter_state_map[(def_dict['parameter']['pgn'], def_dict['parameter']['da'], def_dict['parameter']['sa'], def_dict['parameter']['spn'])] = psmap

        state_parameter_map[state_name] = [state_switch_dict, 0]

        # Finally prepare the state visualizer's startup stuff
        # ~ state_visualizer_map[state_name] = (states['status'],json.dumps(states['definition'], indent=2, separators=(',', ': '), sort_keys=True),len(state_switch_dict))
        state_visualizer_map[state_name] = (states['status'], "", len(state_switch_dict))

        # Increment the position identifier
        identifier = identifier + 1

    return {'to_da_interpreter': pgn_spn_map, 'to_state_indexer': {'parameter_state_map': parameter_state_map,
                                                                   'state_parameter_map': state_parameter_map},
            'to_visualizer': state_visualizer_map}  # , to_gateway': (arb_sa_mask_16,int(arb_sa_mask_16,16))}


def DA_interpreter(pgn_spn_map):
    # Get J1939_DA cursor
    import sqlite3, re, math
    db = sqlite3.connect('J1939-DA.db')
    db.text_factory = str  # This command enables the strings to be decoded by the sqlite commands
    cur = db.cursor()

    def length_byte_to_bit(val):
        if "." not in val:
            val = val + ".1"
        spl = val.split(".")
        return (int(spl[0]) - 1) * 8 + int(spl[1])

    # Interpret DA information and generate masks
    masks = {}
    for pgn_h, spn_map in pgn_spn_map.items():
        tup = []
        for SPNData in cur.execute(
                'SELECT SPN,SPNPOsitioninPGN,SPNLength,Resolution,Offset FROM SPNandPGN WHERE SPNLength <> "" and PGNDOC = "J1939DA" and MultiPacket = "No" AND PGN=' + str(
                    spn_map[0]) + '  AND SPN in (' + ",".join(str(i) for i in list(spn_map[3])) + ')'):
            # let us first get then length
            lsplit = SPNData[2].split(" ")
            length = int(lsplit[0]) if "bit" in lsplit[1] else int(lsplit[0]) * 8
            # Next, let us get the position
            if "-" in SPNData[1]:
                possplit = [x.strip() for x in SPNData[1].split("-")]
            elif "," in SPNData[1]:
                possplit = [x.strip() for x in SPNData[1].split(",")]
            else:
                possplit = [SPNData[1].strip(), "1.1"]
            possplit = [length_byte_to_bit(x) for x in possplit]
            # Now, generate the mask
            mask = 0
            pos = possplit[0]
            # ~ print ("SPN: ", SPNData[0], " Length: ", length, " POS: ", pos)
            for k in range(length):
                mask = mask | 1 << (pos - 1)
                pos = pos + 1
                if pos == (possplit[1] - 1) * 8 + 1:
                    pos = possplit[1]
            # Finally lets parse the resolution and offset
            resolution = ""
            offset = ""
            if (SPNData[3] == "ASCII"):
                resolution = "ASCII"
            elif (SPNData[3] == "Binary" or SPNData[3][-10:] == "bit-mapped"):
                resolution = "bit-mapped"
            else:
                pattern = "^([0-9]*[\.\/][0-9]+|[0-9]+).*"
                res = re.search(pattern, SPNData[3])
                if res:
                    resolution = res.group(1)
                    if "/" in resolution:
                        resolution = float(resolution.split("/")[0]) / float(resolution.split("/")[1])
                    else:
                        resolution = float(resolution)
                per_bit_pattern = "^.*(\/[0-9]+ bit).*$"
                res_morebit = re.search(per_bit_pattern, SPNData[3])
                if res_morebit:
                    num_bits = int(res_morebit.group(1)[1:-4].strip())
                    resolution = resolution / float(math.pow(2, num_bits))

                # ~ offset_pattern = ""
                # ~ off = re.search(offset_pattern, SPNData[4])
                # ~ if off:
                # ~ offset = float(off.group(1))
                offset = float(SPNData[4].split(" ")[0].replace(",", ""))

            tup.append(
                ((spn_map[0], spn_map[1], spn_map[2], int(SPNData[0])), mask, resolution, offset, possplit[0] - 1))

        if len(tup) != len(spn_map[3]):
            raise ValueError('Some SPNs are either Multipacket or not Application Layer or have empty Length factor')
        masks[pgn_h] = tup

    # Release J1939_DA cursor
    cur.close()
    db.close()

    return masks


def communicate(args):
    to_be_returned = {}

    # First let us do the state-reading
    from_state_def_interpreter = state_def_interpreter(args['input_filename'])
    to_be_returned['to_state_indexer'] = from_state_def_interpreter['to_state_indexer']
    to_be_returned['to_visualizer'] = from_state_def_interpreter['to_visualizer']

    # Next, let us get the J1939_Interpreters stuff ready
    to_be_returned['to_J1939_Interpreter'] = DA_interpreter(from_state_def_interpreter['to_da_interpreter'])

    return to_be_returned
