---
title: "Processing"
permalink: /docs/utils/
toc_label: "Table of Contents"
layout: single
---
## Reference for `weblinx.utils`

### `shorten_text`

```
weblinx.utils.shorten_text(s, max_length=100)
```

### `get_nums_from_path`

```
weblinx.utils.get_nums_from_path(path)
```

#### Description

Finds the first and second number in a path. The path should follow the
following pattern: <prefix>-<num_1>-<num_2>.<ext>, e.g. `screenshot-15-1.png`
or `page-15-1.html`, which would return `15` and `1` for both cases.

### `rank_paths`

```
weblinx.utils.rank_paths(path, max_num_2=1, epsilon=1)
```

#### Description

This function can be used to rank file names for sorting purposes. It assumes
the file will follow the following pattern: <prefix>-<num_1>-<num_2>.<ext>, e.g.
`screenshot-15-1.png`. Note that `max_num_2` is used to normalize the second
number, so that the first number is more important. For example, if `max_num_2`
is 10, then the second number will be divided by 10 before being multiplied by
the first number. This means that `screenshot-15-1.png` will be ranked higher.

epsilon is used to ensure that the second part does reach 1.0, which would
make it equal to num_1 + 1, creating an undesired tie.

### `hash_file`

```
weblinx.utils.hash_file(path, method="md5", error_on_missing=True)
```

#### Description

Given a path to a file, this function will return the hash in hex of the file.
It can use either the md5 or sha256 method.

If error_on_missing is True, then this function will raise a FileNotFoundError
if the file does not exist. Otherwise, it will return None.

### `hash_str`

```
weblinx.utils.hash_str(s, method="md5")
```

#### Description

Given a string, this function will return the hash in hex of the string.
It can use either the md5 or sha256 method.

### `hash_json`

```
weblinx.utils.hash_json(data, method="md5")
```

#### Description

Given a json object, this function will return the hash in hex of the json.
It can use either the md5 or sha256 method.

### `hex_to_int`

```
weblinx.utils.hex_to_int(hex_str)
```

#### Description

Given a hex string, this function will return the integer value of the hex.
If there is any non hex character, it will be ignored.

### `load_demo_names_in_split`

```
weblinx.utils.load_demo_names_in_split(split_path, split="train", sample_size=None, random_state=42)
```

#### Description

Loads a split from a json file. The json file should be a dictionary with
keys representing a split name (e.g. train, dev), and the values should be
a list of demo names. This function will return the list of demo names
corresponding to the split name.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `split_path` | `str or Path` |  | The path to the json file containing all the splits. |
| `split` | `str` | `"train"` | The name of the split to load. |
| `sample_size` | `int` | `None` | If not None, then this function will return a random sample of the specified size. |
| `random_state` | `int` | `42` | The random state to use for sampling. |


#### Returns

```
demo_names
```

The list of demo names corresponding to the split. If sample_size is
not None, then this will be a random sample of the specified size.

### `auto_read_json`

```
weblinx.utils.auto_read_json(path, backend="auto")
```

### `auto_save_json`

```
weblinx.utils.auto_save_json(data, path, backend="auto", indent=None)
```

### `save_results`

```
weblinx.utils.save_results(results, result_dir, filename="results.json")
```

### `set_seed`

```
weblinx.utils.set_seed(seed)
```

### `filter_records`

```
weblinx.utils.filter_records(records)
```

#### Description

Given an input `records` (a list of dictionaries), this finds all the records that
match the given kwargs. For example, if records is a list of records
that contain a "demo_name" key and a "turn_index" key, then you can
find all records that match a given demo_name and turn_index by doing
find_record(records, demo_name="demo_1", turn_index=0).

## Reference for `weblinx.utils.envs`

### `get_env_dict`

```
weblinx.utils.envs.get_env_dict(filepath=".env")
```

#### Description

Get environment variables from a .env file.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `filepath` | `str` | `".env"` | The path to the .env file. Defaults to '.env'. |


#### Returns

```
dict
```

A dictionary of environment variables.

### `set_env_vars`

```
weblinx.utils.envs.set_env_vars(filepath=".env")
```

#### Description

Set environment variables from .env file into the current os.environ.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `filepath` | `str` | `".env"` | The path to the .env file. Defaults to '.env'. |


## Reference for `weblinx.utils.format`

### `compose_formatters`

```
weblinx.utils.format.compose_formatters(formatters)
```

#### Description

This function will take a list of formatters and return a function that will
call each formatter in order, and merge the results into a single dictionary.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `formatters` | `list` |  | A list of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |


#### Returns

```
function
```

A function that will call each formatter in order, and merge the results into
a single dictionary.

### `shorten`

```
weblinx.utils.format.shorten(text, max_length=None)
```

#### Description

This function will shorten a text to a maximum length. If the text is shorter
than the maximum length, it will be returned as is. If the text is longer than
the maximum length, it will be truncated and "..." will be added to the end.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `text` | `str` |  | The text to be shortened. |
| `max_length` | `int` | `None` | The maximum length of the text. If the text is longer than this, it will be truncated. Set to None or -1 to disable truncation. |


#### Returns

```
str
```

The shortened text.

### `format_arg_item`

```
weblinx.utils.format.format_arg_item(turn, name, strip=True, max_length=40, return_as="dict")
```

#### Description

This will find a value in the turn's args by the "name", and format it as a
string or a dictionary.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `name` | `str` |  | The name of the argument to be formatted. For example, for the intent "change", the argument name is "value". For the intent "textInput", the argument name is "text". |
| `strip` | `bool` | `True` | Whether to strip the value of the argument. If True, the value will be stripped of leading and trailing whitespaces. If False, the value will not be stripped. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


### `format_output_dictionary`

```
weblinx.utils.format.format_output_dictionary(out_dict, function_key=None, default_function_name="", sep=", ", kv_template="{k}={v}", add_quotes=True, de_escape=True, return_as="str")
```

#### Description

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
        Whether to de-escape newlines (`
`) and tabs (`  `) in the values. This will
        replace `
` with `\n` and `       ` with `\t`, so that they are displayed
        in a single line, allowing the output to fit in a single line.
    return_as: str
        Whether to return the formatted element as a string or a dictionary. This
        should probably be "str", but it is here for consistency with other functions.
        If "dict", it will return the dictionary as is, without any changes.

    Returns
    -------
    

### `format_element`

```
weblinx.utils.format.format_element(turn, include_text=True, include_attrs=True, max_attr_length=20, max_text_length=40, strip_text=True, return_as="dict")
```

#### Description

Format an element into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `include_text` | `bool` | `True` | Whether to include the text of the element, i.e. the textContent attribute. Note it is a bit different from the innerText attribute, but we are not recording the innerText attribute, thus we only use textContent. |
| `include_attrs` | `bool, list or tuple` | `True` | Whether to include the attributes of the element. If True, all the attributes will be included. If False, no attributes will be included. If a list of strings is provided, only the attributes in the list will be included. The key for the attributes will be "attrs". |
| `max_attr_length` | `int` | `20` | The maximum length of any attribute. If the attribute is longer than this, it will be truncated. Set to None or -1 to disable truncation. |
| `max_text_length` | `int` | `40` | The maximum length of the text. If the text is longer than this, it will be truncated. Set to None or -1 to disable truncation. |
| `strip_text` | `bool` | `True` | Whether to strip the text of the element. If True, the text will be stripped of leading and trailing whitespaces. If False, the text will not be stripped. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. If "str", it will be formatted as a string. If "dict", it will be formatted as a dictionary. |


#### Returns

```
formatted
```



#### Example


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

### `format_float`

```
weblinx.utils.format.format_float(value, decimal=0)
```

#### Description

Helpful function to format a float value. This is will either round the value
to the specified number of decimal places, or convert it to an integer if
decimal is 0, or do nothing if decimal is None. If decimal is is not an integer,
it will raise a ValueError.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `value` | `float` |  | The value to be formatted. |
| `decimal` | `int` | `0` | How many digits after decimal point to keep. If 0, the coordinates will be rounded to integers. |


#### Returns

```
float
```

The formatted float value.

#### Raises

ValueError
    If decimal is not an integer.

### `format_mouse_xy`

```
weblinx.utils.format.format_mouse_xy(turn, decimal=0, return_as="dict")
```

#### Description

Get the mouse's x and y coordinates from a turn with intent click.
Those coordinate are with respect to the viewport's dimensions.
This is different from the client's x and y coordinates, which are
relative to the client's dimensions (which can have a different zoom level).

For example, if the viewport is 800x600 and the client is 1600x1200, with a zoom
level of 2, then a mouse at (400, 300) in the client will be at (200, 150) in the
viewport. This function returns the viewport coordinates.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `decimal` | `int` | `0` | How many digits after decimal point to keep. If 0, the coordinates will be rounded to integers. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Example


If return_as is "str", it will return a string like `mouse(x=100, y=200)`.

If return_as is "dict", it will return a dictionary like `{"x": 100, "y": 200}`.

### `format_target_bbox`

```
weblinx.utils.format.format_target_bbox(turn, decimal=0, return_as="dict")
```

#### Description

This function formats the bounding box of the target element
in a turn with intent click or change. The bounding box is
relative to the viewport's dimensions. If the turn does not
have a target element, then the bounding box will be (-1, -1, -1, -1).


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `decimal` | `int` | `0` | How many digits after decimal point to keep. If 0, the coordinates will be rounded to integers. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the bounding box.

### `format_uid`

```
weblinx.utils.format.format_uid(turn, uid_key="data-webtasks-id", return_as="dict")
```

#### Description

This function formats the uid of the target element into the dictionary.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `uid_key` | `str` | `"data-webtasks-id"` | The key to be used to find the element's ID. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the uid.

### `format_timestamp`

```
weblinx.utils.format.format_timestamp(turn, start_time=0, convert_to_minutes=True, time_template="{m:02}:{s:02}", decimal=0, return_as="dict")
```

#### Description

This function formats a timestamp, either in seconds (original) or
in minutes (if convert_to_minutes is True), which is more readable.

If start_time is not 0, then the timestamp will be relative to start_time.
This is because sometimes, the first timestamp is not 0, and could even
be negative to indicate that the event happened before the recording started.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `start_time` | `int or float` | `0` | The start time of the recording, in seconds. If the first timestamp is not 0, then this should be the first timestamp. |
| `convert_to_minutes` | `bool` | `True` | Whether to convert the timestamp to minutes. If True, the timestamp will be converted to minutes, and the formatting will use both the time_template and decimal. If False, the timestamp will be formatted as seconds, and only the decimal will be used. |
| `time_template` | `str` | `"{m:02}:{s:02}"` | The template to be used to format the timestamp. It should have two placeholders, {m} and {s}, which will be replaced by the minutes and seconds. Note that the seconds will have a decimal part, which represents the milliseconds, which will use the decimal. |
| `decimal` | `str` | `0` | The template to be used to format the float values. It should have one placeholder, {v}, which will be replaced by the float value. If None, the float values will not be formatted. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the timestamp.

### `format_change`

```
weblinx.utils.format.format_change(turn, formatters=(<_ast.Name object at 0x7feacdfde4c0>, <_ast.Name object at 0x7feacdfde5b0>, <_ast.Name object at 0x7feacdfde5e0>), return_as="dict")
```

#### Description

This function formats a change event into a readable format.

A change event could be fired, for example, when an radio or checkbox
input is changed. It is different from the input event, which is fired
when the input is changed, for example, in an input, select or textarea.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `formatters` | `` | `(<_ast.Name object at 0x7feacdfde4c0>, <_ast.Name object at 0x7feacdfde5b0>, <_ast.Name object at 0x7feacdfde5e0>)` | A tuple of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

### `format_click`

```
weblinx.utils.format.format_click(turn, formatters=(<_ast.Name object at 0x7feacdfdecd0>, <_ast.Name object at 0x7feacdfdec70>, <_ast.Name object at 0x7feace01d040>), return_as="dict")
```

#### Description

Format a turn with intent click into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `formatters` | `` | `(<_ast.Name object at 0x7feacdfdecd0>, <_ast.Name object at 0x7feacdfdec70>, <_ast.Name object at 0x7feace01d040>)` | A tuple of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

### `format_copy`

```
weblinx.utils.format.format_copy(turn, max_length=200, include_timestamp=True, return_as="dict")
```

#### Description

Format a turn with intent copy into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `max_length` | `int` | `200` | The maximum length of the selected text. If the selected text is longer than this, it will be truncated. Set to None or -1 to disable truncation. |
| `include_timestamp` | `bool` | `True` | True if the timestamp should be included, False otherwise. If a function is provided, it will be called with the turn as the argument and should return a str. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

### `format_paste`

```
weblinx.utils.format.format_paste(turn, max_length=200, include_timestamp=True, return_as="dict")
```

#### Description

Format a turn with intent paste into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `max_length` | `int` | `200` | The maximum length of the selected text. If the selected text is longer than this, it will be truncated. Set to None or -1 to disable truncation. |
| `include_timestamp` | `bool` | `True` | True if the timestamp should be included, False otherwise. If a function is provided, it will be called with the turn as the argument and should return a str. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

### `format_hover`

```
weblinx.utils.format.format_hover(turn, formatters=(<_ast.Name object at 0x7feace004a90>, <_ast.Name object at 0x7feace004ac0>, <_ast.Name object at 0x7feace004af0>), return_as="dict")
```

#### Description

This behaves similarly to format_click, but for hover events.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `formatters` | `list or tuple` | `(<_ast.Name object at 0x7feace004a90>, <_ast.Name object at 0x7feace004ac0>, <_ast.Name object at 0x7feace004af0>)` | A tuple of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


### `format_load`

```
weblinx.utils.format.format_load(turn, max_length=60, include_timestamp=True, include_transition=True, join_qualifiers="; ", return_as="dict")
```

#### Description

Format a turn with intent load into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `max_length` | `int` | `60` | The maximum length of the url. If the url is longer than this, it will be truncated. Set to None or -1 to disable truncation. |
| `include_timestamp` | `bool` | `True` | True if the timestamp should be included, False otherwise. If a function is provided, it will be called with the turn as the argument and should return a str. |
| `include_transition` | `bool` | `True` | True if the transition type and qualifiers should be included, False otherwise. More information about the transition type and qualifiers can be found in the notes section below. |
| `join_qualifiers` | `str` | `"; "` | The string to be used to join the qualifiers. If None, the qualifiers will not be joined. Only used if include_transition is True. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn. A dict will have the following keys:
- intent: "load"
- url: the url of the page
- type: the type of transition, e.g. "link", "typed", "reload"
- qualifiers: a list of qualifiers, e.g. ["from_address_bar", "forward_back"]

#### Notes

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

### `format_say`

```
weblinx.utils.format.format_say(turn, include_timestamp=True, max_length=200, return_as="dict")
```

#### Description

This function formats a turn where the type is chat instead of browser.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `include_timestamp` | `bool` | `True` | True if the timestamp should be included, False otherwise. If a function is provided, it will be called with the turn as the argument and should return a str. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

#### Example

If return_as is "str", it will return a string like:
```
say(speaker="instructor", utterance="Hello!")
```

If return_as is "dict", it will return a dictionary like:
```
{"intent": "say", "speaker": "instructor", "utterance": "Hello!"}
```.

### `format_scroll`

```
weblinx.utils.format.format_scroll(turn, decimal=0, include_timestamp=True, return_as="dict")
```

#### Description

Similar to format_mouse_xy, but for scroll events.

### `format_submit`

```
weblinx.utils.format.format_submit(turn, formatters=(<_ast.Name object at 0x7feace0245b0>, <_ast.Name object at 0x7feace0245e0>), return_as="dict")
```

#### Description

Format a turn with intent submit into a readable format.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `formatters` | `` | `(<_ast.Name object at 0x7feace0245b0>, <_ast.Name object at 0x7feace0245e0>)` | A tuple of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


### `format_tab`

```
weblinx.utils.format.format_tab(turn, return_as="dict")
```

#### Description

Format a turn with intent tabcreate, tabremove or tabswitch into a readable format.

### `format_text_input`

```
weblinx.utils.format.format_text_input(turn, formatters=(<_ast.Name object at 0x7feace033ca0>, <_ast.Name object at 0x7feace033df0>, <_ast.Name object at 0x7feace033f10>), return_as="dict")
```

#### Description

This function formats a text input event into a readable format.

Input event is fired when the value is changed in an input, select or textarea.
It is different from the change event, which is fired when an radio or checkbox input
is changed.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | The turn object to be represented as either a string or a dictionary. |
| `formatters` | `` | `(<_ast.Name object at 0x7feace033ca0>, <_ast.Name object at 0x7feace033df0>, <_ast.Name object at 0x7feace033f10>)` | A tuple of functions to be used to format the turn. The functions will be called in order, and each function should return a dictionary (not a string), which will be merged into the final output. The functions should take the turn as the first argument, and return a dictionary. |
| `return_as` | `str` | `"dict"` | Whether to return the formatted element as a string or a dictionary. |


#### Returns

```
formatted
```

A string or dictionary representing the turn.

### `format_intent_automatically`

```
weblinx.utils.format.format_intent_automatically(turn, format_change=<_ast.Name object at 0x7feace039c40>, format_click=<_ast.Name object at 0x7feace039c70>, format_copy=<_ast.Name object at 0x7feace039ca0>, format_hover=<_ast.Name object at 0x7feace039cd0>, format_load=<_ast.Name object at 0x7feace039d00>, format_paste=<_ast.Name object at 0x7feace039d30>, format_say=<_ast.Name object at 0x7feace039d60>, format_scroll=<_ast.Name object at 0x7feace039d90>, format_submit=<_ast.Name object at 0x7feace039dc0>, format_tab=<_ast.Name object at 0x7feace039df0>, format_text_input=<_ast.Name object at 0x7feace039e20>, return_as="dict")
```

#### Description

This function will format a turn automatically, depending on the intent.
This relies on mapping the turn's intent to a function that formats the turn,
e.g. "click" will be mapped to format_click, "change" will be mapped to
format_change, etc.


#### Raises

ValueError
    If the intent is not recognized.

## Reference for `weblinx.utils.html`

### `has_elem_in_viewport`

```
weblinx.utils.html.has_elem_in_viewport(turn, attrib_dict, key="data-webtasks-id", min_height=2, min_width=2, verbose=False)
```

#### Description

Given a turn and an element's attributes, check if the element is in the viewport.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `webtasks.Turn` |  | The turn to check. |
| `attrib_dict` | `dict` |  | The element's attributes, as a dictionary. If you use lxml.html, you can get this by calling `elem.attrib`. For bs4, you can get this by calling `elem.attrs`. For example: `{"data-webtasks-id": "1234", "class": "foo bar"}` |
| `key` | `str` | `"data-webtasks-id"` | The key to use to find the element's ID. |
| `min_height` | `int` | `2` | The minimum height of the element to be considered in the viewport. Defaults to 2. |
| `min_width` | `int` | `2` | The minimum width of the element to be considered in the viewport. Defaults to 2. |
| `verbose` | `bool` | `False` | Whether to print out debug statements. Defaults to False. |


### `open_html_with_encodings`

```
weblinx.utils.html.open_html_with_encodings(path, encodings=['"utf-8"', '"latin-1"'], raise_error=True)
```

#### Description

Open an HTML file with a list of encodings.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `path` | `str` |  | The path to the HTML file. |
| `encodings` | `list` | `['"utf-8"', '"latin-1"']` | A list of encodings to try. Defaults to ["utf-8", "latin-1"]. |
| `raise_error` | `bool` | `True` | Whether to raise an error if the file cannot be opened. Defaults to True. If False, returns None if the file cannot be opened. |


#### Returns

```
lxml.html.HtmlElement
```

The HTML element.

### `filter_bboxes`

```
weblinx.utils.html.filter_bboxes(bboxes, min_height=10, min_width=10, viewport_height=None, viewport_width=None)
```

#### Description

Given the bboxes of a turn, filter out bboxes if:
- The bbox is smaller than the minimum height and minimum width (one of them must be satisfied)
- The bbox is outside the viewport (if viewport_height or viewport_width is not None)


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `bboxes` | `dict` |  | The bboxes of the turn. |
| `min_height` | `int` | `10` | The minimum height of the bbox. Defaults to 10. |
| `min_width` | `int` | `10` | The minimum width of the bbox. Defaults to 10. |
| `viewport_height` | `int` | `None` | The height of the viewport. If not None, then bboxes with y > viewport_height are filtered out. Defaults to None. |
| `viewport_width` | `int` | `None` | The width of the viewport. If not None, then bboxes with x > viewport_width are filtered out. Defaults to None. |


#### Returns

```
dict
```

The filtered bboxes that satisfy the conditions.s

## Reference for `weblinx.utils.hydra`

### `resolve_cache_path`

```
weblinx.utils.hydra.resolve_cache_path(cfg)
```

#### Description

Assuming we have the following:
- cfg.data.cache : controls whether to read/write from cache or not
- cfg.data.cache_dir : the directory to store the cache file, if cache=True
- cfg.data.cache_filename : the name of the cache file, if cache=True
- cfg.data.load_file_from_cache : controls whether to load from cache or not

This will return the path to the cache file and load_from_cache_file boolean.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `cfg` | `dict` |  | The configuration object. It must be a hydrated OmegaConf object. |


#### Returns

```
tuple[str, bool]
```

The path to the cache file and the load_from_cache_file boolean.

### `save_path_to_hydra_logs`

```
weblinx.utils.hydra.save_path_to_hydra_logs(save_dir, save_name="hydra_path.txt")
```

#### Description

This helper function saves the path to the hydra logs into the model directory.
This is useful for archival purposes.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `save_dir` | `str` |  | The directory to save the hydra path to. |
| `save_name` | `str` | `"hydra_path.txt"` | The name of the file to save the hydra path to. |


## Reference for `weblinx.utils.recs`

### `is_list_monotonically_increasing`

```
weblinx.utils.recs.is_list_monotonically_increasing(lst)
```

#### Description

This function checks if a list is monotonically increasing.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `lst` | `list` |  | The list to check. |


#### Returns

```
bool
```

True if the list is monotonically increasing, False otherwise.

### `get_list_from_records_by_key`

```
weblinx.utils.recs.get_list_from_records_by_key(records, key)
```

#### Description

For a given key, return a list of values from the records
taken from the key.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `records` | `dict` |  | A list of dictionaries to extract the values from. |
| `key` | `str` |  | The key to extract from the records. |


#### Returns

```
list
```

A list of values from the records based on the key.

### `insert_list_into_records_by_key`

```
weblinx.utils.recs.insert_list_into_records_by_key(records, key, lst)
```

#### Description

Given a records and a list, both of the same length, insert the list into the records
based on the key. For example, we have:
```
records = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4},
    {"a": 5, "b": 6},
]
lst = [10, 20, 30]
```

Then, we we can use this function to insert each element of the list into the records
based on the key:
```
insert_list_into_records_by_key(records, "c", lst)
```

This will result in:
```
records = [
    {"a": 1, "b": 2, "c": 10},
    {"a": 3, "b": 4, "c": 20},
    {"a": 5, "b": 6, "c": 30},
]
```


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `records` | `dict` |  | A list of dictionaries to insert the list into. |
| `key` | `str` |  | The key to insert the list into. |
| `lst` | `list` |  | The list to insert into the records. |


### `group_record_to_dict`

```
weblinx.utils.recs.group_record_to_dict(records, keys, remove_keys=False, copy=True)
```

#### Description

Given a list of dictionaries, this function groups the dictionaries by the
keys specified in `keys`. The keys in `keys` must be present in all
dictionaries. The end result is a dictionary of dictionaries, where the
key is a tuple of (val1, val2, ...) corresponding to key1, key2, etc.,
and the value is a subset of the original list of dictionaries.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `records` | `List[dict] (List)` |  | A list of dictionaries to be grouped. |
| `keys` | `List[str]` |  | The keys to group by. They must be present in all dictionaries. |
| `remove_keys` | `bool` | `False` | Whether to remove the keys from the dictionaries in the output. |
| `copy` | `bool` | `True` | Whether to copy the dictionaries in the output before returning. If False, then the dictionaries of the input records will be modified in place. |


### `ungroup_dict_to_records`

```
weblinx.utils.recs.ungroup_dict_to_records(grouped_records, restore_keys=None)
```

#### Description

Given a dictionary of grouped records, this function restores the keys
specified in `restored_keys` and returns a list of dictionaries. If the
`restored_keys` is None, then the keys are not restored.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `grouped_records` | `dict` |  | A dictionary of grouped records, which means the keys are tuples and the values are lists of dictionaries. |
| `restore_keys` | `list` | `None` | The keys to restore. If None, then the keys are not restored. |


#### Returns

```
list
```

A list of dictionaries.

#### Example


Here's an example of how this function works. Suppose we have a dictionary:
```
{
    ("foo", "bar"): [
        {"c": 1, "d": 2},
        {"c": 3, "d": 4},
        # ...
    ],
    # ...
}
```

Then, if `restored_keys=None`, the output will be:
```
[
    {"c": 1, "d": 2},
    {"c": 3, "d": 4},
    # ...
]
```

If `restored_keys=["a", "b"]`, then the output will be:
```
[
    {"a": "foo", "b": "bar", "c": 1, "d": 2},
    {"a": "foo", "b": "bar", "c": 3, "d": 4},
    # ...
]
```

## Reference for `weblinx.utils.url`

### `shorten_url`

```
weblinx.utils.url.shorten_url(url, width=50, placeholder="[...]")
```

### `remove_subdomain`

```
weblinx.utils.url.remove_subdomain(url)
```

#### Description

Given a url, remove the subdomain part, if the subdomain is not in domains_allowed

### `calculate_length_of_tld`

```
weblinx.utils.url.calculate_length_of_tld(url)
```

#### Description

Given a url, calculate the length of the top level domain.
In general, the length of tld is 1, e.g. .com, .org, .net, etc.

However, there are some exceptions, e.g. .co.uk, .co.nz, etc.
We want to return >1 for these cases.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `url` | `str` |  | The url from which to calculate the length of the tld. |


#### Returns

```
int
```

The length of the tld.

### `has_valid_tld`

```
weblinx.utils.url.has_valid_tld(url)
```

#### Description

Given a url, check if it has a valid tld. If it does, return True, else False.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `url` | `str` |  | The url to check. |


#### Returns

```
bool
```

True if the url has a valid tld, else False.

## Reference for `weblinx.utils.video`

#### `Viewport.from_metadata`

```
weblinx.utils.video.Viewport.from_metadata(cls, metadata)
```

##### Description

Returns a new Viewport from the metadata of a turn.

#### `Viewport.from_numpy`

```
weblinx.utils.video.Viewport.from_numpy(cls, array)
```

#### `Viewport.from_pillow`

```
weblinx.utils.video.Viewport.from_pillow(cls, im)
```

#### `Viewport.from_cv2`

```
weblinx.utils.video.Viewport.from_cv2(cls, cap)
```

#### `Viewport.from_video_path`

```
weblinx.utils.video.Viewport.from_video_path(cls, video_path)
```

#### `Viewport.scale`

```
weblinx.utils.video.Viewport.scale(self, zoom_level)
```

##### Description

Returns a new Viewport with the scaled height and width based on the zoom level.

#### `CropArea.crop_numpy`

```
weblinx.utils.video.CropArea.crop_numpy(self, array)
```

##### Description

Crops a numpy array. based on the crop area (x_start, x_end, y_start, y_end)


##### Note

Numpy arrays of images have shape [h, w] (i.e. [row, column]), and the correspondance is
w -> x and h -> y, so coordinates in an array are represented as [y, x].

### `get_initial_viewport`

```
weblinx.utils.video.get_initial_viewport(replay)
```

### `get_crop_area`

```
weblinx.utils.video.get_crop_area(full, cropped)
```

#### Description

Given two viewports (full and cropped), return the start and end indices such that
the cropped viewport is a subset of the full viewport. The start and end indices
are in the form of (h, w) and start from the bottom right.

Here's a diagram:

full shape:
    ```
    oooo
    oooo
    oooo
    ```

cropped shape:
    ```
    xxx
    xxx
    ```

End results (after cropping based on the o and x shapes)
    ```
    oooo
    rrro
    rrro
    ```

Where `r` indicates the area that remains after cropping. This returns a CropArea
object that can be used to crop the numpy array of an image (see `CropArea.crop_numpy`).

### `find_starting_frame`

```
weblinx.utils.video.find_starting_frame(cap_or_path, crop_area=None, delay=5, min_redness=0.9, max_greenness=0.1, max_blueness=0.1, callback=None)
```

#### Description

Given a video capture, start and end viewports, and a delay, find the index of the
first frame that matches the criteria. The criteria is based on the average color
of the frame. The delay is used to skip the first part of the video (before the
extension is activated).


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `cap_or_path` | `str, Path, or cv2.VideoCapture (Union)` |  | If this is a string or a Path, we will create a new video capture object from that path. If it's a video capture object, we will use that object (but we will roll back the frame index to 0 and not close the object). |
| `crop_area` | `CropArea` | `None` | The area of the frame to crop. This is used to crop the frame before checking the average color. If `crop_area=None`, the whole frame will be used. |
| `delay` | `int` | `5` | The number of seconds to continue after the first red frame is found. This is because we want to use the LAST red frame, not the first one, and a delay allows us to wait until the last red frame is found. |
| `min_redness` | `float` | `0.9` | The minimum average redness of the frame. Higher values mean more red pixels. This is used to detect the frame with mostly red pixels. |
| `max_greenness` | `float` | `0.1` | The maximum average greenness of the frame. Lower values mean less green pixels. This is used to avoid frames that have a lot of pixels with a high average on the green channel (e.g. white screens). |
| `max_blueness` | `float` | `0.1` | The maximum average blueness of the frame. Lower values mean less blue pixels. This is used to avoid frames that have a lot of pixels with a high average on the blue channel (e.g. white screens). |
| `callback` | `callable` | `None` | A function that is called for each frame. It receives the index of the frame and the frame itself. It has the signature `callback(i: int, num_frames: int, frame: np.array)`. This is useful to track the progress of the function or to display the frame to the user. If  you can leave it as `None` if you don't need it. |


#### Returns

```
int
```

The index of the first frame that matches the criteria. You can access that frame via
`cap.set(cv2.CAP_PROP_POS_FRAMES, idx)`.

### `get_start_frame`

```
weblinx.utils.video.get_start_frame(demo, load_from_processed_metadata=True, save_to_processed_metadata=True, callback=None, delay=5)
```

#### Description

This is a high-level function that wraps `find_starting_frame`, `get_initial_viewport`,
and `get_crop_area` to find the starting frame of a demo. It also saves the starting
frame to the processed metadata file of the demo, and can reload it from there if
`load_from_processed_metadata=True`. This allows a concise way to get the starting
frame of a demo (without having to wait for the expensive `find_starting_frame` to
run every time).


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `demo` | `Demo` |  | The demo to get the starting frame of. |
| `load_from_processed_metadata` | `bool` | `True` | Whether to load the starting frame from the processed metadata file of the demo. This will read the processed_metadata.json file in the demo's path and return the value of the "start_frame" key if it exists. If it doesn't exist, it will run `find_starting_frame` and save the result to the processed metadata file. |
| `save_to_processed_metadata` | `bool` | `True` | Whether to save the starting frame to the processed metadata file of the demo. This will save the starting frame to the processed_metadata.json file in the demo's path. |
| `callback` | `callable` | `None` | A function that is called for each frame. It receives the index of the frame and the frame itself. It has the signature `callback(i: int, num_frames: int, frame: np.array)`. This is useful to track the progress of the function or to display the frame to the user. If  you can leave it as `None` if you don't need it. |
| `delay` | `int` | `5` | The number of seconds to continue after the first red frame is found. This is because we want to use the LAST red frame, not the first one, and a delay allows us to wait until the last red frame is found. |


#### Returns

```
int
```

The index of the starting frame of the demo.

### `get_fps`

```
weblinx.utils.video.get_fps(video_path)
```

#### Description

Given a video path, return the FPS of the video.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `video_path` | `str` |  | The path to the video file. |


#### Returns

```
float
```

The FPS of the video.

### `get_frame`

```
weblinx.utils.video.get_frame(video_path, frame_number)
```

#### Description

Given a video_path and a frame number, return the frame.
Behind the scenes, this uses OpenCV to read the frame, convert to RGB,
and return the frame as a numpy array.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `video_path` | `str` |  | The path to the video file. |
| `frame_number` | `int` |  | The frame number to read. |


#### Returns

```
np.array
```

The frame as a numpy array. The shape is (h, w, 3) and the dtype is uint8.

### `timestamp_to_frame_num`

```
weblinx.utils.video.timestamp_to_frame_num(timestamp, fps, force_floor=True)
```

#### Description

Given a timestamp and the FPS of the video, return the frame number.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `timestamp` | `int` |  | The timestamp of the frame in seconds. |
| `fps` | `float` |  | The FPS of the video. This can be obtained by calling `get_fps`. |
| `force_floor` | `bool` | `True` | Whether to round the frame number down (floor) or not. This is set to True by default because one might get a float frame number due to the timestamp conversion, and rounding it down makes more sense than rounding it to closest, because the previously frame is still displayed at the time of the timestamp (i.e. the frame is not yet changed). |


### `frame_num_to_timestamp`

```
weblinx.utils.video.frame_num_to_timestamp(frame_num, fps)
```

#### Description

Given a frame number and the FPS of the video, return the timestamp.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `frame_num` | `int` |  | The frame number. |
| `fps` | `float` |  | The FPS of the video. This can be obtained by calling `get_fps`. |


#### Returns

```
float
```

The timestamp of the frame in seconds.

### `draw_bbox`

```
weblinx.utils.video.draw_bbox(im, intent, bbox, inplace=False, convert_to_rgb=True)
```

#### Description

Draw the bounding box of the element targeted by the action on an image.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `im` | `PIL.Image` |  | The image to draw on. This image will be modified in place unless `copy` is True. |
| `intent` | `str` |  | The type of event. It must be one of "click", "hover", "textInput", or "change". You can obtain it by calling `turn.intent`. |
| `bbox` | `dict` |  | The bounding box of the element targeted by the action. You can obtain it by calling `turn.element.get("bbox")`. |
| `inplace` | `bool` | `False` | Whether to modify the image in place or return a copy. |
| `convert_to_rgb` | `bool` | `True` | Whether to convert the image to RGB at the end. This is useful for saving to JPEG. |


#### Returns

```
PIL.Image
```

The image with the overlay drawn on it.

### `draw_at_xy`

```
weblinx.utils.video.draw_at_xy(im, intent, x, y, inplace=False, convert_to_rgb=True)
```

#### Description

Draw a red dot at some action's x and y coordinates on the image. This is only
relevant when the intent is "click" or "hover".


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `im` | `PIL.Image` |  | The image to draw on. This image will be modified in place unless `copy` is True. |
| `intent` | `str` |  | The type of event. It must be one of "click", "hover", "textInput", or "change". You can obtain it by calling `turn.intent`. |
| `x` | `int` |  | The x coordinate of the action. You can obtain it by calling `turn.props.get("x")`. |
| `y` | `int` |  | The y coordinate of the action. You can obtain it by calling `turn.props.get("y")`. |
| `inplace` | `bool` | `False` | Whether to modify the image in place or return a copy. |
| `convert_to_rgb` | `bool` | `True` | Whether to convert the image to RGB at the end. This is useful for saving to JPEG. |


#### Returns

```
PIL.Image
```

The image with the overlay drawn on it.

