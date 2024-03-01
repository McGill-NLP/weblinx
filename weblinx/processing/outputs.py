"""
This file is used to process the results, run the evaluation metrics, and generate the output CSV tables.
"""
import logging
import math
from typing import TYPE_CHECKING

from .intent import Intent

if TYPE_CHECKING:
    from .. import Turn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def are_not_none(*args):
    return all(arg is not None for arg in args)


def cast_to_float(value):
    """
    Checks if a value is an int or a float.
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

    try:
        return float(value)
    except ValueError:
        return None


def format_action_arg_value(arg_value):
    arg_value = arg_value.strip()
    # If starts and/or ends with ", remove them
    if arg_value.startswith('"') and arg_value.endswith('"'):
        arg_value = arg_value[1:-1]
    # otherwise, it is not a string, so convert to int or float
    if "." in arg_value:
        try:
            arg_value = float(arg_value)
        except ValueError:
            pass

    elif arg_value.isdigit():
        arg_value = int(arg_value)

    elif arg_value.startswith("-") and arg_value[1:].isdigit():
        arg_value = int(arg_value)

    return arg_value

def list_all_non_alphanum_chars(other_chars_allowed: list = None):
    """
    Returns a list of all non-alphanumeric characters in Python.
    """
    if other_chars_allowed is None:
        other_chars_allowed = []
    
    other_chars_allowed = set(other_chars_allowed)
    return [chr(i) for i in range(0, 256) if not chr(i).isalnum() or chr(i) in other_chars_allowed]

def split_by_comma(string: str, check_quotes: bool = False) -> list:
    """
    This function splits a string by commas, but ignores commas inside quotes.
    For example, if my string is 'a, b, "c, d", e', then this function will return
    ['a', 'b', '"c, d"', 'e'] if check_quotes is True, but ['a', 'b', '"c', 'd"', 'e']
    if check_quotes is False.

    Example
    -------
    ```python
    # Let's test the function
    test_string = 'a, b, "c, d", e'
    print(split_by_comma(test_string, check_quotes=True))
    print(split_by_comma(test_string, check_quotes=False))
    ```
    """
    # First, split by comma
    split = string.split(",")

    # If check_quotes is False, return the split
    if not check_quotes:
        return split

    # Otherwise, we need to merge the elements that are inside quotes
    merged = []
    for s in split:
        if not merged:
            merged.append(s)
        elif merged[-1].count('"') % 2 == 0:
            merged.append(s)
        else:
            merged[-1] += "," + s

    return merged


def find_last_non_alphanum_char(s, other_chars_allowed: list = None):
    """
    Given a string and a list of characters, find the last index of a non-alphanumeric character in the string.
    """
    if other_chars_allowed is None:
        other_chars_allowed = []
    other_chars_allowed = set(other_chars_allowed)
    
    for i in range(len(s) - 1, -1, -1):
        if not (s[i].isalnum() or s[i] in other_chars_allowed):
            return i
    return -1

def find_intent_and_raw_args(raw_output_string: str) -> dict:
    """
    This iterative function will walk through a raw string that might contain an action
    in the form `intent(arg1="val1", arg2=num1, ...)` and return the intent and the unparsed args
    """
    # Find the first bracket open
    ix_bracket_open = raw_output_string.find("(")
    if ix_bracket_open == -1:
        return "", ""
    
    # Look at the first non-whitespace character between the start of the string and the first bracket
    # Starting from the right side
    before = raw_output_string[:ix_bracket_open]
    intent_start_ix = find_last_non_alphanum_char(before, other_chars_allowed=["_"]) + 1
    
    intent = raw_output_string[intent_start_ix:ix_bracket_open].strip()
    
    # Now, we need to find the closing bracket. However, we need to be careful that there might be
    # brackets nested inside the arguments between two quotes, so we need to keep track of the number
    # of open and closing quotes
    quote_is_open = False
    ix_bracket_close = len(raw_output_string)
    for i in range(ix_bracket_open, len(raw_output_string)):
        if raw_output_string[i] == '"':
            quote_is_open = not quote_is_open
        elif raw_output_string[i] == ")" and not quote_is_open:
            ix_bracket_close = i
            break
    
    # Now, we can take the substring between the brackets, which will be our raw args
    raw_args = raw_output_string[ix_bracket_open + 1:ix_bracket_close]
    
    return intent, raw_args
    
    

def parse_predicted_output_string(raw_output_string: str) -> dict:
    """
    Given an output string, try to find a substring of format <intent>(<key1>=<value1>, <key2>=<value2>, ...) and return a dictionary of format:
    {
        "intent": <intent>,
        "key1": <value1>,
        "key2": <value2>,
        ...
    }
    Returns None if the parsing fails.
    """
    
    # Sanity check: test this string
    # raw = 'text_input(text="oh no ):", uid="123")'
    raw_intent, raw_args = find_intent_and_raw_args(raw_output_string)

    # Split by comma that are not inside quotes
    args = split_by_comma(raw_args, check_quotes=True)
    # Split by =
    args = [arg.strip().partition("=") for arg in args if "=" in arg]

    # Create a dictionary from args
    args = {
        arg_key.strip(): format_action_arg_value(arg_value)
        for arg_key, sep, arg_value in args
    }
    intent = Intent.from_string(raw_intent)

    if intent == Intent.ACTION:
        # This is the generation "action" intent for m2w, in this case the intent is in the args
        if "intent" in args:
            intent = Intent.from_string(args["intent"])
        else:
            intent = Intent.UNKNOWN

    if intent == Intent.UNKNOWN:
        preview = raw_output_string[:100].replace("\n", "\\n")
        logger.warning(f"Unknown intent '{raw_intent}': {preview}")

    return intent, args


def get_element_info(
    turn: 'Turn',
    uid,
    uid_key="data-webtasks-id",
    cache_dir=".cache/demonstrations/xpaths",
):
    """
    Given a uid_key for an element, retrieve additional information about the element from the HTML which can be used for evaluation.

    Extracts only the information needed for evaluation.
    """
    if not uid:
        return None

    xpaths_dict = turn.get_xpaths_dict(cache_dir=cache_dir)

    if len(xpaths_dict) == 0:
        return None

    if uid not in xpaths_dict:
        return None

    if turn.bboxes is None or uid not in turn.bboxes:
        return None

    element_info = {
        "attributes": {
            uid_key: uid,
        },
        "bbox": turn.bboxes[uid],
        "xpath": xpaths_dict[uid],
    }

    return element_info


def get_element_uid_by_coords(turn: "Turn", x, y):
    """
    Given (x,y) coordinates for an element, find the smallest non-zero-sized element that contains the coordinates using bboxes and return its id.
    """
    bboxes = turn.bboxes

    if not bboxes:
        return None

    # find the smallest element that contains the coordinates
    min_elem_size = None
    elem_uid = None

    for uid, bbox in bboxes.items():
        left = math.floor(bbox["left"])
        right = math.ceil(bbox["right"])
        top = math.floor(bbox["top"])
        bottom = math.ceil(bbox["bottom"])
        if left <= x <= right and top <= y <= bottom:
            elem_size = bbox["width"] * bbox["height"]

            if elem_size == 0:
                continue

            if min_elem_size is None or elem_size < min_elem_size:
                min_elem_size = bbox["width"] * bbox["height"]
                elem_uid = uid

    return elem_uid


def get_xy_coords_corners(args):
    if not all(isinstance(args[k], int) for k in ["top", "left", "right", "bottom"]):
        return None

    x = (args["left"] + args["right"]) / 2
    y = (args["top"] + args["bottom"]) / 2

    return x, y


def dict_has_keys(d, keys):
    """
    Checks if a dictionary has all the keys in a list.
    """
    return all([key in d for key in keys])


def infer_element_for_action(intent, args, turn: "Turn", uid_key="data-webtasks-id"):
    """
    Given an intent and args, infer the element that the action is performed on, if
    the element is not explicitly specified.
    """
    element = None

    if intent in Intent.get_element_intents(as_set=True):
        # find the referenced element
        if "uid" in args:
            uid = args["uid"]

        elif uid_key in args:
            uid = args[uid_key]

        elif "x" in args and "y" in args:
            if args["x"] is None or args["y"] is None:
                uid = None
            else:
                uid = get_element_uid_by_coords(turn, args["x"], args["y"])

        elif dict_has_keys(args, ["top", "left", "right", "bottom"]):
            coords = get_xy_coords_corners(args)
            if coords is not None:
                x, y = coords
                uid = get_element_uid_by_coords(turn, x, y)
            else:
                uid = None

        else:
            uid = None

        if uid is not None:
            element = get_element_info(turn, uid)

    return element


def extract_action_from_turn(turn: "Turn", uid_key="data-webtasks-id"):
    """
    Creates an action from a turn in a demonstration (i.e. the ground truth action).
    """
    element = None
    intent = None
    args = {}

    if turn.type == "chat":
        intent = Intent.SAY
        args["speaker"] = turn["speaker"]
        args["utterance"] = turn["utterance"]

    elif turn.type == "browser":
        intent = Intent.from_string(turn.intent)
        if turn.element:
            wid = turn.element.get("attributes", {}).get(uid_key)
            if wid is not None:
                element = get_element_info(turn, wid)
            else:
                # if it is not possible (e.g. because of missing bounding boxes),
                # use the element as it is saved in the turn
                element = turn.element

                # drop unnecessary fields
                for key in ["innerHTML", "outerHTML", "textContent"]:
                    if key in element:
                        element.pop(key)

        if intent == Intent.TEXT_INPUT:
            args["text"] = turn.args["text"]
        elif intent == Intent.CHANGE:
            args["value"] = turn.args["value"]
        elif intent == Intent.LOAD:
            args["url"] = turn.props.get("url") or turn.args.get("url")
        elif intent == Intent.SCROLL:
            args["x"] = turn.args["scrollX"]
            args["y"] = turn.args["scrollY"]
        elif intent == Intent.COPY:
            args["text"] = turn.args["selected"]
        elif intent == Intent.PASTE:
            args["text"] = turn.args["pasted"]
        elif intent == Intent.TAB_REMOVE:
            args["tab_id"] = turn.props["tabId"]
        elif intent == Intent.TAB_SWITCH:
            args["tab_id_from"] = turn.props["tabIdOrigin"]
            args["tab_id_to"] = turn.props["tabId"]
        elif intent in [
            Intent.TAB_CREATE,
            Intent.CLICK,
            Intent.HOVER,
            Intent.SUBMIT,
        ]:
            # no other args, so we can just skip
            pass
        else:
            logger.error(f"Unknown intent: {intent}")

    return {
        "intent": intent,
        "args": args,
        "element": element,
    }


def sanitize_args(args):
    """
    This function is used to sanitize the arguments of an action.
    """
    # First, we ensure that x and y are floats, otherwise we convert them to None
    if "x" in args and "y" in args:
        args["x"] = cast_to_float(args["x"])
        args["y"] = cast_to_float(args["y"])

    # If only one of x or y is present, we first check if there was a parsing
    # issue where y was bundled with x or vice versa, if not we set both to None
    if "x" in args and "y" not in args:
        if isinstance(args["x"], str) and "y=" in args["x"]:
            args["x"], _, args["y"] = args["x"].partition("y=")
            args["x"] = cast_to_float(args["x"])
            args["y"] = cast_to_float(args["y"])
        else:
            args["x"] = None
            args["y"] = None

    elif "y" in args and "x" not in args:
        if isinstance(args["y"], str) and "x=" in args["y"]:
            args["y"], _, args["x"] = args["y"].partition("x=")
            args["x"] = cast_to_float(args["x"])
            args["y"] = cast_to_float(args["y"])
        else:
            args["x"] = None
            args["y"] = None

    # Then, we ensure that top, left, right, and bottom are ints, otherwise we convert them to None
    for key in ["top", "left", "right", "bottom"]:
        if key in args:
            args[key] = cast_to_float(args[key])

    return args


def check_pred_is_suitable(pred):
    """
    Given a prediction, check if it is suitable for evaluation.
    """
    # We simply check if the intent is one of the intents that we evaluate
    return pred["intent"] in Intent.get_eval_intents(as_set=True)
