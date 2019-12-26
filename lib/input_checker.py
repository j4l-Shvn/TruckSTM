import json, jsonschema as jsc
import sys

# The schema for state def files
schema = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "description": "A state",
        "properties": {
            "name": {"description": "A good name for the state", "type": "string"},
            "status": {"type": "string", "enum": ["Normal", "Abnormal"]},
            "definition": {"description": "The actual definition as set of parameter instances",
                           "type": "array",
                           "minItems": 1,
                           "items": {
                               "type": "object",
                               "properties": {
                                   "parameter": {"description": "Parameter identifiers",
                                                 "type": "object",
                                                 "properties": {
                                                     "pgn": {"type": "integer"}, "da": {"type": "integer"},
                                                     "sa": {"type": "integer"}
                                                 },
                                                 "required": ["pgn", "da", "sa"]
                                                 },
                                   "pinstset": {"description": "Parameter instance sets",
                                                "type": "array",
                                                "items": {"type": "pinst"}
                                                },
                                   "timeout": {
                                       "description": "The parameter will be set to unavailable if not received by this timeout",
                                       "type": "tmout"},
                                   "comment": {"description": "A comment about the parameter instance",
                                               "type": "string"}
                               },
                               "required": ["parameter", "pinstset"]
                           }
                           }
        },
        "required": ["name", "status", "definition"]
    }
}


def binary_format_checker(inp):
    return 1 <= len(set(inp).union({'0', '1'})) <= 2


def ASCII_format_checker(inp):
    for c in inp:
        if ord(c) > 127:
            return False
    return True


def pinst_format_checker(checker, inp):
    if isinstance(inp, list):
        return len(inp) == 2 and inp[0] < inp[1]
    else:
        if isinstance(inp, str):
            return ASCII_format_checker(inp) or binary_format_checker(inp)
        else:
            return isinstance(inp, int) or isinstance(inp, float)


def tmout_format_checker(checker, inp):  # format either "X[1-10]" or \d+
    return (isinstance(inp, str) and (inp.startswith("X") and int(inp[1:], 10) <= 10)) or (isinstance(inp, int))


type_checker = jsc.Draft7Validator.TYPE_CHECKER.redefine("pinst", pinst_format_checker).redefine("tmout",
                                                                                                 tmout_format_checker)
CustomValidator = jsc.validators.extend(jsc.Draft7Validator, type_checker=type_checker)
validator = CustomValidator(schema=schema)


def validate_state_defs(states_from_file):
    try:
        validator.validate(states_from_file)
        print("Valid state definition")
    except jsc.exceptions.ValidationError as v:
        print("State-def json not valid: ", v)
        sys.exit(1)
