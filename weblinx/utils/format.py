"""
This utility module mainly aims at formatting turns and replays into readable formats.
For example, it can format a turn with intent click into a readable format, like this:
click("<button>Click me</button>", x=100, y=200).
"""

from datetime import datetime
from functools import partial
from typing import Callable


def _validate_return_as(return_as):
    if return_as not in ["str", str, "dict", dict]:
        raise ValueError(
            f"return_as must be either 'str' or 'dict', but got {return_as}"
        )
    if return_as is str:
        return_as = "str"
    elif return_as is dict:
        return_as = "dict"

    return return_as


def _validate_intent(turn, *intents):
    if turn.intent not in intents:
        raise ValueError(
            f"The intent provided was {turn.intent}, but expected one of: {list(intents)}"
        )


def compose_formatters(formatters: list) -> Callable:
    """
    This function will take a list of formatters and return a function that will
    call each formatter in order, and merge the results into a single dictionary.

    Parameters
    ----------
    formatters : list
        A list of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    Returns
    -------
    function
        A function that will call each formatter in order, and merge the results into
        a single dictionary.
    """

    def formatter(turn: "Turn") -> dict:
        output = {}
        for f in formatters:
            output.update(f(turn))
        return output

    return formatter


def shorten(text: str, max_length: int = None) -> str:
    """
    This function will shorten a text to a maximum length. If the text is shorter
    than the maximum length, it will be returned as is. If the text is longer than
    the maximum length, it will be truncated and "..." will be added to the end.

    Parameters
    ----------
    text : str
        The text to be shortened.

    max_length : int
        The maximum length of the text. If the text is longer than this, it will be
        truncated. Set to None or -1 to disable truncation.

    Returns
    -------
    str
        The shortened text.
    """
    if max_length in [None, -1]:
        return text

    if len(text) <= max_length:
        return text

    if max_length <= 3:
        return text[:max_length]

    return text[: max_length - 3] + "..."


def format_arg_item(turn, name, strip=True, max_length=40, return_as="dict"):
    """
    This will find a value in the turn's args by the "name", and format it as a
    string or a dictionary.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    name: str
        The name of the argument to be formatted. For example, for the intent
        "change", the argument name is "value". For the intent "textInput",
        the argument name is "text".

    strip : bool
        Whether to strip the value of the argument. If True, the value will be stripped
        of leading and trailing whitespaces. If False, the value will not be stripped.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.
    """
    return_as = _validate_return_as(return_as)

    value = turn.args.get(name, "")

    if strip:
        value = value.strip()

    output = {name: shorten(value, max_length=max_length)}

    if return_as == "str":
        return output[name]  # We simply return the value
    else:
        return output


def format_output_dictionary(
    out_dict,
    function_key=None,
    default_function_name="",
    sep=", ",
    kv_template="{k}={v}",
    add_quotes=True,
    de_escape=True,
    return_as="str",
):
    """
    This will display a dictionary as a string in the format of a function call.
    For example, given a dict like:
    ```
    {'tag': 'span', 'attrs': {'class': 'd-button-label',...}, 'text': 'Log In'}
    ```

    We could display it as (with function_key="tag"):
    ```
    span(attrs={'class': 'd-button-label',...}, text='Log In')
    ```

    Parameters
    ----------
    out_dict : dict
        The dictionary to be formatted.

    function_key : str
        The key to be used as the function name. It should be a key in the dictionary,
        and the value of that key will be used as the function name. For example, if
        function_key is "tag", then the value of d["tag"] will be used, such as "span".

    default_function_name : str
        The default function name to be used if function_key is None or not in the
        dictionary. If this is None, then an error will be raised if function_key is
        None or not in the dictionary.

    sep : str
        The separator to be used to join the key-value pairs.

    kv_template : str
        The template to be used to format each key-value pair. It should have two
        placeholders, {k} and {v}, which will be replaced by the key and value.

    add_quotes : bool
        Whether to add quotes (`"`) to strings in the values.

    de_escape : bool
        Whether to de-escape newlines (`\n`) and tabs (`\t`) in the values. This will
        replace `\n` with `\\n` and `\t` with `\\t`, so that they are displayed
        in a single line, allowing the output to fit in a single line.
    return_as: str
        Whether to return the formatted element as a string or a dictionary. This
        should probably be "str", but it is here for consistency with other functions.
        If "dict", it will return the dictionary as is, without any changes.

    Returns
    -------
    """
    if not isinstance(out_dict, dict):
        raise ValueError(f"d must be a dict, but got '{type(out_dict)}'")

    if return_as == "dict":
        return out_dict

    if function_key is not None and not isinstance(function_key, str):
        raise ValueError(
            f"function_key must be a string, but got '{type(function_key)}'"
        )

    d_without_text = {k: v for k, v in out_dict.items() if k != function_key}

    if function_key is None:
        function_name = default_function_name
    elif function_key not in out_dict:
        if default_function_name is None:
            raise ValueError(
                f"function_key must be a key in d, but got '{function_key}'"
            )
        else:
            function_name = default_function_name
    else:
        function_name = out_dict[function_key]

    if add_quotes:
        d_without_text = {
            k: f'"{v}"' if isinstance(v, str) else v for k, v in d_without_text.items()
        }
    if de_escape:
        d_without_text = {
            k: v.replace("\n", "\\n").replace("\t", "\\t") if isinstance(v, str) else v
            for k, v in d_without_text.items()
        }
    joined = sep.join([kv_template.format(k=k, v=v) for k, v in d_without_text.items()])

    return f"{function_name}({joined})"


def format_element(
    turn,
    include_text=True,
    include_attrs=True,
    max_attr_length=20,
    max_text_length=40,
    strip_text=True,
    return_as="dict",
):
    """
    Format an element into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    include_text : bool
        Whether to include the text of the element, i.e. the textContent attribute.
        Note it is a bit different from the innerText attribute, but we are not
        recording the innerText attribute, thus we only use textContent.

    include_attrs : bool, list or tuple
        Whether to include the attributes of the element. If True, all the attributes
        will be included. If False, no attributes will be included. If a list of
        strings is provided, only the attributes in the list will be included.
        The key for the attributes will be "attrs".

    max_attr_length : int
        The maximum length of any attribute. If the attribute is longer
        than this, it will be truncated. Set to None or -1 to disable truncation.

    max_text_length : int
        The maximum length of the text. If the text is longer than this, it will be
        truncated. Set to None or -1 to disable truncation.

    strip_text : bool
        Whether to strip the text of the element. If True, the text will be stripped
        of leading and trailing whitespaces. If False, the text will not be stripped.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.
        If "str", it will be formatted as a string. If "dict", it will be formatted
        as a dictionary.

    Returns
    -------
    formatted : str or dict

    Example
    --------

    Here's an example of a formatted element as a dictionary:
    ```
    {
        "tag": "button",
        "attrs": {
            "id": "my-button",
            # ...
        },
        "text": "Click me",
    }
    ```
    """
    return_as = _validate_return_as(return_as)

    if turn.element is None:
        return None

    output = {}

    # First, let's add tag
    output["tag"] = turn.element["tagName"].lower()

    # Let's now add attributes
    if include_attrs is True:
        attrs = turn.element["attributes"]
    elif isinstance(include_attrs, list):
        attrs = {
            k: v for k, v in turn.element["attributes"].items() if k in include_attrs
        }
    else:
        attrs = {}

    attrs = {k: shorten(v, max_length=max_attr_length) for k, v in attrs.items()}
    output["attrs"] = attrs

    # Finally, let's add text
    if include_text:
        tc = turn.element["textContent"]
        if strip_text:
            tc = tc.strip()
        output["text"] = shorten(tc, max_length=max_text_length)

    return format_output_dictionary(output, function_key="tag", return_as=return_as)


def format_float(value, decimal=0):
    """
    Helpful function to format a float value. This is will either round the value
    to the specified number of decimal places, or convert it to an integer if
    decimal is 0, or do nothing if decimal is None. If decimal is is not an integer,
    it will raise a ValueError.

    Parameters
    ----------
    value : float
        The value to be formatted.

    decimal : int
        How many digits after decimal point to keep. If 0, the coordinates will be
        rounded to integers.

    Returns
    -------
    float
        The formatted float value.

    Raises
    ------
    ValueError
        If decimal is not an integer.
    """
    if decimal is None:
        pass
    elif decimal == 0:
        value = int(value)
    elif isinstance(decimal, int):
        value = round(value, decimal)
    else:
        raise ValueError(f"decimal must be an integer or `None`, but got {decimal}.")
    return value


def format_mouse_xy(turn, decimal=0, return_as="dict"):
    """
    Get the mouse's x and y coordinates from a turn with intent click.
    Those coordinate are with respect to the viewport's dimensions.
    This is different from the client's x and y coordinates, which are
    relative to the client's dimensions (which can have a different zoom level).

    For example, if the viewport is 800x600 and the client is 1600x1200, with a zoom
    level of 2, then a mouse at (400, 300) in the client will be at (200, 150) in the
    viewport. This function returns the viewport coordinates.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    decimal : int
        How many digits after decimal point to keep. If 0, the coordinates will be
        rounded to integers.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Example
    -------

    If return_as is "str", it will return a string like `mouse(x=100, y=200)`.

    If return_as is "dict", it will return a dictionary like `{"x": 100, "y": 200}`.
    """
    return_as = _validate_return_as(return_as)

    if "mouseX" not in turn.metadata or "mouseY" not in turn.metadata:
        x = -1
        y = -1
    else:
        x = turn.metadata["mouseX"]
        y = turn.metadata["mouseY"]

    output = {
        "x": format_float(x, decimal=decimal),
        "y": format_float(y, decimal=decimal),
    }

    return format_output_dictionary(
        output, default_function_name="mouse", return_as=return_as
    )


def format_target_bbox(turn, decimal: int = 0, return_as: str = "dict"):
    """
    This function formats the bounding box of the target element
    in a turn with intent click or change. The bounding box is
    relative to the viewport's dimensions. If the turn does not
    have a target element, then the bounding box will be (-1, -1, -1, -1).

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    decimal : int
        How many digits after decimal point to keep. If 0, the coordinates will be
        rounded to integers.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the bounding box.
    """
    bboxes = turn.element.get("bbox", {})
    if len(bboxes) == 0:
        output = {"top": -1, "left": -1, "right": -1, "bottom": -1}

    output = {
        "top": format_float(bboxes["top"], decimal=decimal),
        "left": format_float(bboxes["left"], decimal=decimal),
        "right": format_float(bboxes["right"], decimal=decimal),
        "bottom": format_float(bboxes["bottom"], decimal=decimal),
    }

    return format_output_dictionary(
        output, default_function_name="bounding_box", return_as=return_as
    )


def format_uid(turn, uid_key="data-webtasks-id", return_as="dict"):
    """
    This function formats the uid of the target element into the dictionary.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    uid_key : str
        The key to be used to find the element's ID.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the uid.
    """
    output = {"uid": turn.element.get("attributes", {}).get(uid_key, None)}

    return format_output_dictionary(output, return_as=return_as)


def format_timestamp(
    turn,
    start_time=0,
    convert_to_minutes=True,
    time_template="{m:02}:{s:02}",
    decimal=0,
    return_as="dict",
):
    """
    This function formats a timestamp, either in seconds (original) or
    in minutes (if convert_to_minutes is True), which is more readable.

    If start_time is not 0, then the timestamp will be relative to start_time.
    This is because sometimes, the first timestamp is not 0, and could even
    be negative to indicate that the event happened before the recording started.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    start_time : int or float
        The start time of the recording, in seconds. If the first timestamp is not 0,
        then this should be the first timestamp.

    convert_to_minutes : bool
        Whether to convert the timestamp to minutes. If True, the timestamp will be
        converted to minutes, and the formatting will use both the time_template and
        decimal. If False, the timestamp will be formatted as seconds, and
        only the decimal will be used.

    time_template : str
        The template to be used to format the timestamp. It should have two
        placeholders, {m} and {s}, which will be replaced by the minutes and seconds.
        Note that the seconds will have a decimal part, which represents the
        milliseconds, which will use the decimal.

    decimal : str
        The template to be used to format the float values. It should have one
        placeholder, {v}, which will be replaced by the float value. If None, the
        float values will not be formatted.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the timestamp.
    """
    return_as = _validate_return_as(return_as)

    timestamp = turn.timestamp - start_time

    if convert_to_minutes:
        if timestamp < 0:
            negative = True
            mins = int((-timestamp) // 60)
            secs = (-timestamp) % 60
        else:
            negative = False
            mins = int(timestamp // 60)
            secs = timestamp % 60

        secs = format_float(secs, decimal=decimal)

        timestamp = time_template.format(m=mins, s=secs)

        if negative:
            timestamp = "-" + timestamp

    else:
        timestamp = format_float(timestamp, decimal=decimal)

    if return_as == "str":
        return timestamp
    else:
        return {"timestamp": timestamp}


# INTENT FORMATTING STARTS HERE


def format_change(
    turn,
    formatters=(
        partial(format_arg_item, name="value"),
        format_element,
        format_timestamp,
    ),
    return_as="dict",
):
    """
    This function formats a change event into a readable format.

    A change event could be fired, for example, when an radio or checkbox
    input is changed. It is different from the input event, which is fired
    when the input is changed, for example, in an input, select or textarea.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    formatters:
        A tuple of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "change")

    output = compose_formatters(formatters)(turn)
    output["intent"] = output.get("intent", "change")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_click(
    turn,
    formatters=(
        format_mouse_xy,
        format_element,
        format_timestamp,
    ),
    return_as="dict",
):
    """
    Format a turn with intent click into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.
    formatters:
        A tuple of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "click")
    output = compose_formatters(formatters)(turn)
    output["intent"] = output.get("intent", "click")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_copy(turn, max_length=200, include_timestamp=True, return_as="dict"):
    """
    Format a turn with intent copy into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    max_length : int
        The maximum length of the selected text. If the selected text is longer than
        this, it will be truncated. Set to None or -1 to disable truncation.

    include_timestamp : bool
        True if the timestamp should be included, False otherwise. If a function is
        provided, it will be called with the turn as the argument and should return a str.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "copy")

    output = {
        "intent": "copy",
        "text": shorten(turn.args["selected"], max_length=max_length),
    }

    if include_timestamp is True:
        output["timestamp"] = format_timestamp(turn, return_as="str")
    elif callable(include_timestamp):
        output["timestamp"] = include_timestamp(turn)

    if return_as == "str":
        return format_output_dictionary(output, function_key="intent")
    else:
        return output


def format_paste(turn, max_length=200, include_timestamp=True, return_as="dict"):
    """
    Format a turn with intent paste into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    max_length : int
        The maximum length of the selected text. If the selected text is longer than
        this, it will be truncated. Set to None or -1 to disable truncation.

    include_timestamp : bool
        True if the timestamp should be included, False otherwise. If a function is
        provided, it will be called with the turn as the argument and should return a str.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "paste")

    output = {
        "intent": "paste",
        "text": shorten(turn.args["pasted"], max_length=max_length),
    }

    if include_timestamp is True:
        output["timestamp"] = format_timestamp(turn, return_as="str")
    elif callable(include_timestamp):
        output["timestamp"] = include_timestamp(turn)

    if return_as == "str":
        return format_output_dictionary(output, function_key="intent")
    else:
        return output


def format_hover(
    turn,
    formatters=(format_mouse_xy, format_element, format_timestamp),
    return_as="dict",
):
    """
    This behaves similarly to format_click, but for hover events.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    formatters: list or tuple
        A tuple of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "hover")

    output = compose_formatters(formatters)(turn)
    output["intent"] = output.get("intent", "hover")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_load(
    turn,
    max_length=60,
    include_timestamp=True,
    include_transition=True,
    join_qualifiers="; ",
    return_as="dict",
):
    """
    Format a turn with intent load into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    max_length : int
        The maximum length of the url. If the url is longer than this, it will be
        truncated. Set to None or -1 to disable truncation.

    include_timestamp : bool
        True if the timestamp should be included, False otherwise. If a function is
        provided, it will be called with the turn as the argument and should return a str.

    include_transition: bool
        True if the transition type and qualifiers should be included, False otherwise.
        More information about the transition type and qualifiers can be found in the
        notes section below.

    join_qualifiers: str
        The string to be used to join the qualifiers. If None, the qualifiers will not
        be joined. Only used if include_transition is True.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn. A dict will have the following keys:
        - intent: "load"
        - url: the url of the page
        - type: the type of transition, e.g. "link", "typed", "reload"
        - qualifiers: a list of qualifiers, e.g. ["from_address_bar", "forward_back"]

    Notes
    -----
    The (transition) type and (transition) qualifiers are concepts of the Chrome Browser.
    You can read more about them on the [official documentation](https://developer.chrome.com/docs/extensions/reference/webNavigation/)

    The following qualifiers are possible:
        - from_address_bar
        - forward_back
        - client_redirect
        - server_redirect

    The following types are possible:
        - link
        - typed
        - auto_bookmark
        - auto_subframe
        - manual_subframe
        - generated
        - start_page
        - form_submit
        - reload
        - keyword
        - keyword_generated
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "load")

    url = turn.props.get("url") or turn.get("url")
    url = shorten(url, max_length=max_length)

    output = {"intent": "load", "url": url}

    if include_transition:
        if "transitionType" in turn.props:
            output["type"] = turn.props["transitionType"]

        if "transitionQualifiers" in turn.props:
            output["qualifiers"] = turn.props["transitionQualifiers"]

        if join_qualifiers is not None and "qualifiers" in output:
            output["qualifiers"] = join_qualifiers.join(output["qualifiers"])

    if include_timestamp is True:
        output["timestamp"] = format_timestamp(turn, return_as="str")
    elif callable(include_timestamp):
        output["timestamp"] = include_timestamp(turn)

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_say(turn, include_timestamp=True, max_length=200, return_as="dict"):
    """
    This function formats a turn where the type is chat instead of browser.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    include_timestamp : bool
        True if the timestamp should be included, False otherwise. If a function is
        provided, it will be called with the turn as the argument and should return a str.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.

    Example
    --------
    If return_as is "str", it will return a string like:
    ```
    say(speaker="instructor", utterance="Hello!")
    ```

    If return_as is "dict", it will return a dictionary like:
    ```
    {"intent": "say", "speaker": "instructor", "utterance": "Hello!"}
    ```.
    """
    return_as = _validate_return_as(return_as)
    # Instead of turn.intent, we check for turn.type in the case of say
    if turn.type != "chat":
        raise ValueError(f"Turn type must be chat, but got {turn.type}")

    # Get the speaker

    output = {
        "intent": "say",
        "speaker": turn["speaker"],
        "utterance": shorten(turn["utterance"], max_length=max_length),
    }

    if include_timestamp is True:
        output["timestamp"] = format_timestamp(turn, return_as="str")
    elif callable(include_timestamp):
        output["timestamp"] = include_timestamp(turn)

    if return_as == "str":
        return format_output_dictionary(output, function_key="intent")
    else:
        return output


def format_scroll(turn, decimal=0, include_timestamp=True, return_as="dict"):
    """
    Similar to format_mouse_xy, but for scroll events.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "scroll")

    x = format_float(turn.args["scrollX"], decimal=decimal)
    y = format_float(turn.args["scrollY"], decimal=decimal)

    output = dict(intent=turn.intent, x=x, y=y)

    if include_timestamp:
        output["timestamp"] = format_timestamp(turn, return_as="str")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_submit(
    turn, formatters=(format_element, format_timestamp), return_as="dict"
):
    """
    Format a turn with intent submit into a readable format.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    formatters:
        A tuple of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "submit")

    output = compose_formatters(formatters)(turn)

    output["intent"] = output.get("intent", "submit")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_tab(turn, return_as="dict"):
    """
    Format a turn with intent tabcreate, tabremove or tabswitch into a readable format.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "tabcreate", "tabremove", "tabswitch")

    output = {
        "intent": turn.intent,
    }

    if "tabIdOrigin" in turn.props:
        output["origin"] = turn.props.get("tabIdOrigin")

    output["target"] = turn.props.get("tabId", "Unknown")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_text_input(
    turn,
    formatters=(
        partial(format_arg_item, name="text"),
        partial(format_element, include_text=False),
        format_timestamp,
    ),
    return_as="dict",
):
    """
    This function formats a text input event into a readable format.

    Input event is fired when the value is changed in an input, select or textarea.
    It is different from the change event, which is fired when an radio or checkbox input
    is changed.

    Parameters
    ----------
    turn : Turn
        The turn object to be represented as either a string or a dictionary.

    formatters:
        A tuple of functions to be used to format the turn. The functions will be
        called in order, and each function should return a dictionary (not a string),
        which will be merged into the final output. The functions should take the
        turn as the first argument, and return a dictionary.

    return_as : str
        Whether to return the formatted element as a string or a dictionary.

    Returns
    -------
    formatted : str or dict
        A string or dictionary representing the turn.
    """
    return_as = _validate_return_as(return_as)
    _validate_intent(turn, "textInput")

    output = compose_formatters(formatters)(turn)
    output["intent"] = output.get("intent", "text_input")

    return format_output_dictionary(output, function_key="intent", return_as=return_as)


def format_intent_automatically(
    turn,
    format_change: Callable = format_change,
    format_click: Callable = format_click,
    format_copy: Callable = format_copy,
    format_hover: Callable = format_hover,
    format_load: Callable = format_load,
    format_paste: Callable = format_paste,
    format_say: Callable = format_say,
    format_scroll: Callable = format_scroll,
    format_submit: Callable = format_submit,
    format_tab: Callable = format_tab,
    format_text_input: Callable = format_text_input,
    return_as="dict",
):
    """
    This function will format a turn automatically, depending on the intent.
    This relies on mapping the turn's intent to a function that formats the turn,
    e.g. "click" will be mapped to format_click, "change" will be mapped to
    format_change, etc.

    Raises
    ------
    ValueError
        If the intent is not recognized.
    """
    return_as = _validate_return_as(return_as)
    intent_to_function = {
        "change": format_change,
        "click": format_click,
        "copy": format_copy,
        "hover": format_hover,
        "load": format_load,
        "paste": format_paste,
        "scroll": format_scroll,
        "submit": format_submit,
        "tabcreate": format_tab,
        "tabremove": format_tab,
        "tabswitch": format_tab,
        "textInput": format_text_input,
    }

    if turn.type == "chat":
        return format_say(turn, return_as=return_as)

    if turn.intent not in intent_to_function:
        accepted = list(intent_to_function.keys()) + ["say"]
        raise ValueError(
            f"Intent {turn.intent} not recognized. Make sure it is one of: {accepted}"
        )

    return intent_to_function[turn.intent](turn, return_as=return_as)
