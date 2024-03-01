---
title: "WebLINX"
permalink: /docs/core/
toc_label: "Table of Contents"
layout: single
---
## Reference for `weblinx`

### `format_repr`

```
weblinx.format_repr(cls)
```

#### Description

Generate a __repr__ method for a class with the given attributes

### `Demonstration`

```
weblinx.Demonstration(name, base_dir="./demonstrations", json_backend="auto")
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `name` | `str` |  | Name of the demonstration directory |
| `base_dir` | `str` | `"./demonstrations"` | Base directory containing all demonstrations directories |
| `json_backend` | `str` | `"auto"` | Backend to use to load JSON files. Can be either 'auto', 'json', 'orjson', or 'ujson'. For the 'auto' option, it will try to import 'orjson' first, then 'ujson', then 'json'. Both 'orjson' and 'ujson' are faster than 'json', but they must be installed first, via `pip install orjson` or `pip install ujson`. |


#### `Demonstration.__repr__`

```
weblinx.Demonstration.__repr__(self)
```

#### `Demonstration.metadata`

```
weblinx.Demonstration.metadata(self)
```

##### Description

Returns the metadata dictionary, which contains the following keys:
    - recordingEnd: end time of the demonstration
    - recordingEndISO: end time of the demonstration in ISO format
    - recordingId: unique ID of the demonstration
    - recordingStart: start time of the demonstration
    - recordingStartISO: start time of the demonstration in ISO format
    - timezoneOffsetMinutes: timezone offset in minutes
    - user: user
    - userAgent: whether
    - version: version of the demonstration

#### `Demonstration.replay`

```
weblinx.Demonstration.replay(self)
```

##### Description

Returns the replay dictionary with two keys:
    - data: list of data points
    - version: version of the demonstration


##### Note

If you want a `Replay` object, call `Replay.from_demonstration(demo)`.

#### `Demonstration.form`

```
weblinx.Demonstration.form(self)
```

##### Description

Returns the form dictionary, which contains the form dictionary with the following keys:
    - annotator: name of the annotator
    - description: description of the demonstration
    - tasks: list of tasks
    - navigator_name: name of the navigator
    - instructor_name: name of the instructor
    - shortcode: randomly generated unique shortcode to identify the demonstration
    - upload_date: date when the demonstration was uploaded

#### `Demonstration.has_file`

```
weblinx.Demonstration.has_file(self, filename)
```

##### Description

Check if a file exists in the demonstration directory

#### `Demonstration.is_valid`

```
weblinx.Demonstration.is_valid(self, check_invalid_file=True)
```

##### Description

Verifies that the demonstration directory is valid by
checking that all required files exist.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `check_invalid_file` | `bool` | `True` | Whether to check if the demonstration has an invalid.json file. |


#### `Demonstration.load_json`

```
weblinx.Demonstration.load_json(self, filename, backend=None, default=None)
```

##### Description

Load a JSON file from the demonstration directory


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `filename` | `str` |  | Name of the file to load |
| `backend` | `str` | `None` | Backend to use to load the JSON file. Can be either None, 'auto', 'json', 'orjson', or 'ujson'. If 'auto', it will try to import 'orjson' first, then 'ujson', then 'json'. If None, it will use the json_backend specified in the constructor. |
| `default` | `Any` | `None` | Default value to return if the file does not exist. If None, it will raise an error. |


#### `Demonstration.save_json`

```
weblinx.Demonstration.save_json(self, obj, filename, overwrite=False, indent=2)
```

##### Description

Saves an object to the demonstration directory. If it's a string,
it will be saved as-is. If it's a dictionary, it will be saved as
a JSON file.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `obj` | `Union[str, dict] (Union)` |  | Object to save. If it's a string, it will be saved as-is. If it's a dictionary, it will be saved as a JSON file. |
| `filename` | `str` |  | Name of the file to save the object to. |
| `overwrite` | `bool` | `False` | Whether to overwrite the file if it already exists. If False, the file will not be overwritten and the function will return the path to the existing file. |


#### `Demonstration.get_version`

```
weblinx.Demonstration.get_version(self, as_tuple=True)
```

##### Description

Returns the version of the demonstration as a string or tuple

#### `Demonstration.get_recording_path`

```
weblinx.Demonstration.get_recording_path(self, format="mp4", prefix="video", return_str=True)
```

##### Description

Returns the path to the recording file

format: format of the recording file
prefix: prefix of the recording file
return_str: whether to return a string instead of a Path object

#### `Demonstration.get_screenshot_path`

```
weblinx.Demonstration.get_screenshot_path(self, name, return_str=True)
```

##### Description

Returns the path to the screenshot file

index: index of the screenshot
return_str: whether to return a string instead of a Path object

#### `Demonstration.get_upload_date`

```
weblinx.Demonstration.get_upload_date(self, as_datetime=False)
```

##### Description

Returns the upload date of the demonstration as a string or datetime object

#### `Demonstration.list_all_screenshots`

```
weblinx.Demonstration.list_all_screenshots(self, return_str=True)
```

##### Description

Returns a list of all screenshots (including ones not in the replay)

#### `Demonstration.list_all_html_pages`

```
weblinx.Demonstration.list_all_html_pages(self, return_str=True)
```

##### Description

Returns a list of all HTML files (including ones not in the replay)

#### `Demonstration.join`

```
weblinx.Demonstration.join(self)
```

##### Description

Joins the demonstration path with the given arguments.


##### Example

```
demo = wt.Demonstration('...')

html_path = demo.join('pages', 'page-1-0.html')
```

### `Turn`

```
weblinx.Turn(turn_dict, index, demo_name, base_dir, json_backend="auto")
```

#### Description

This class represents a turn in a demonstration, and can be used as a dictionary.

#### `Turn.__repr__`

```
weblinx.Turn.__repr__(self)
```

#### `Turn.from_replay`

```
weblinx.Turn.from_replay(cls, replay, index)
```

##### Description

Returns a Turn object from a replay and an index

#### `Turn.args`

```
weblinx.Turn.args(self)
```

##### Description

Arguments of the turn. This is a shortcut to access the arguments
of the action, which is nested under action -> arguments. It
returns None if the turn is not a browser turn.

#### `Turn.type`

```
weblinx.Turn.type(self)
```

##### Description

Type of the turn, either 'browser' or 'extension'

#### `Turn.timestamp`

```
weblinx.Turn.timestamp(self)
```

##### Description

Number of seconds since the start of the demonstration

#### `Turn.intent`

```
weblinx.Turn.intent(self)
```

##### Description

If the turn is a browser turn, returns the intent of the action, otherwise returns None

#### `Turn.metadata`

```
weblinx.Turn.metadata(self)
```

##### Description

If the turn is a browser turn, returns the metadata of the action, otherwise returns None


##### Note

The metadata is nested under action -> arguments -> metadata, so this property
is a shortcut to access it.

#### `Turn.url`

```
weblinx.Turn.url(self)
```

##### Description

If the turn is a browser turn, returns the URL of the action, otherwise returns None


##### Note

The URL is nested under action -> arguments -> metadata -> url, so this property
is a shortcut to access it.

#### `Turn.tab_id`

```
weblinx.Turn.tab_id(self)
```

##### Description

If the turn is a browser turn, returns the tab ID of the action, otherwise returns `None`.
The tab ID is an integer that uniquely identifies a tab in the browser. If tab_id == -1,
then it means there was no tab ID associated with the action (e.g. if the action was to
delete a tab); in contrast, `tab_id` being `None` means that the turn did not have a
action metadata.


##### Note

The tab ID is nested under action -> arguments -> metadata -> tabId, so this property
is a shortcut to access it.

#### `Turn.viewport_height`

```
weblinx.Turn.viewport_height(self)
```

##### Description

If the turn is a browser turn, returns the viewport height of the action, otherwise returns `None`.
The viewport height is an integer that represents the height of the viewport in the browser.

#### `Turn.viewport_width`

```
weblinx.Turn.viewport_width(self)
```

##### Description

If the turn is a browser turn, returns the viewport width of the action, otherwise returns `None`.
The viewport width is an integer that represents the width of the viewport in the browser.

#### `Turn.mouse_x`

```
weblinx.Turn.mouse_x(self)
```

##### Description

If the turn is a browser turn, returns the mouse X position of the action, otherwise returns `None`.
The mouse X position is an integer that represents the X position of the mouse in the browser.

#### `Turn.mouse_y`

```
weblinx.Turn.mouse_y(self)
```

##### Description

If the turn is a browser turn, returns the mouse Y position of the action, otherwise returns `None`.
The mouse Y position is an integer that represents the Y position of the mouse in the browser.

#### `Turn.client_x`

```
weblinx.Turn.client_x(self)
```

##### Description

If the turn is a browser turn, returns the client X position of the action, otherwise returns `None`.
The client X is the mouse X position scaled with zoom.

#### `Turn.client_y`

```
weblinx.Turn.client_y(self)
```

##### Description

If the turn is a browser turn, returns the client Y position of the action, otherwise returns `None`.
The client Y is the mouse Y position scaled with zoom.

#### `Turn.zoom`

```
weblinx.Turn.zoom(self)
```

##### Description

If the turn is a browser turn, returns the zoom level of the action, otherwise returns `None`.
The zoom level is a float that represents how much the page is zoomed in or out.

#### `Turn.element`

```
weblinx.Turn.element(self)
```

##### Description

If the turn is a browser turn, returns the element of the action, otherwise returns None


##### Example


Here's an example of the element of a click action:

```json
{
    "attributes": {
        // ...
        "data-webtasks-id": "4717de80-eda2-4319",
        "display": "block",
        "type": "submit",
        "width": "100%"
    },
    "bbox": {
        "bottom": 523.328125,
        "height": 46,
        "left": 186.5,
        "right": 588.5,
        "top": 477.328125,
        "width": 402,
        "x": 186.5,
        "y": 477.328125
    },
    "innerHTML": "Search",
    "outerHTML": "<button width="100%" ...>Search</button>",
    "tagName": "BUTTON",
    "textContent": "Search",
    "xpath": "id("root")/main[1]/.../button[1]"
}
```



##### Note

The element is nested under action -> arguments -> element, so this property
is a shortcut to access it.

#### `Turn.props`

```
weblinx.Turn.props(self)
```

##### Description

If the turn is a browser turn, returns the properties of the action, otherwise returns None.


##### Example


Here's an example of the properties of a click action:
```json
{
    "altKey": false,
    "button": 0,
    "buttons": 1,
    "clientX": 435,
    "clientY": 500,
    // ...
    "screenX": 435,
    "screenY": 571,
    "shiftKey": false,
    "timeStamp": 31099.899999976158,
    "x": 435,
    "y": 500
}
```


##### Note

The props is nested under action -> arguments -> properties, so this property
is a shortcut to access it.

#### `Turn.bboxes`

```
weblinx.Turn.bboxes(self)
```

##### Description

This uses the path returned by `self.get_bboxes_path()` to load the bounding boxes of the turn,
and parse them with JSON to return a dictionary, or return None if the path is invalid. It relies
on the default parameters of `self.get_bboxes_path()` to get the path to the bounding boxes.


##### Note

If you want to change the default parameters, you can call `self.get_bboxes_path()` with the
desired parameters and then load the JSON file yourself:

```
import json

turns = wt.Replay.from_demonstrations(demo).filter_if_html_page()

path = turns[0].get_bboxes_path(subdir="bboxes", page_subdir="pages")

with open(path) as f:
    bboxes = json.load(f)
```

#### `Turn.html`

```
weblinx.Turn.html(self)
```

##### Description

This uses the path returned by `self.get_html_path()` to load the HTML of the turn,
and return it as a string, or return None if the path is invalid. It relies on the
default parameters of `self.get_html_path()` to get the path to the HTML page.


##### Example

You can use this with BeautifulSoup to parse the HTML:

```
from bs4 import BeautifulSoup
turns = wt.Replay.from_demonstrations(demo).filter_if_html_page()
soup = BeautifulSoup(turns[0].html, "html.parser")
```

If you want to change the default parameters, you can call `self.get_html_path()` with the
desired parameters and then load the HTML file yourself:

```
turns = wt.Replay.from_demonstrations(demo).filter_if_html_page()
with open(turns[0].get_html_path(subdir="pages")) as f:
    html = f.read()
```

#### `Turn.format_text`

```
weblinx.Turn.format_text(self, max_length=50)
```

##### Description

This returns a string representation of the action or utterance. In the case of action
we have a combination of the tag name, text content, and intent, with the format:
`[tag] text -> INTENT: arg`.

If it is a chat turn, we have a combination of the speaker and utterance, with the format:
`[say] utterance -> SPEAKER`.


##### Example


If the action is a click on a button with the text "Click here", the output will be:
```
[button] Click here -> CLICK
```

If the action is to input the word "world" in a text input that already has the word "Hello":
```
[input] Hello -> TEXTINPUT: world
```

#### `Turn.validate`

```
weblinx.Turn.validate(self)
```

##### Description

This checks if the following keys are present:
- type
- timestamp

Additionally, it must have one of the following combinations:
- action, state
- speaker, utterance

#### `Turn.has_screenshot`

```
weblinx.Turn.has_screenshot(self)
```

##### Description

Returns True if the turn has a screenshot, False otherwise

#### `Turn.has_html`

```
weblinx.Turn.has_html(self)
```

##### Description

Returns True if the turn has an associated HTML page, False otherwise

#### `Turn.has_bboxes`

```
weblinx.Turn.has_bboxes(self, subdir="bboxes", page_subdir="pages")
```

##### Description

Checks if the turn has bounding boxes

#### `Turn.get_screenshot_path`

```
weblinx.Turn.get_screenshot_path(self, subdir="screenshots", return_str=True, throw_error=True)
```

##### Description

Returns the path to the screenshot of the turn, throws an error if the turn does not have a screenshot


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `subdir` | `str` | `"screenshots"` | Subdirectory of the demonstration directory where the HTML pages are stored. |
| `return_str` | `bool` | `True` | If True, returns the path as a string, otherwise returns a Path object |
| `throw_error` | `bool` | `True` | If True, throws an error if the turn does not have an HTML page, otherwise returns None |


#### `Turn.get_html_path`

```
weblinx.Turn.get_html_path(self, subdir="pages", return_str=True, throw_error=True)
```

##### Description

Returns the path to the HTML page of the turn.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `subdir` | `str` | `"pages"` | Subdirectory of the demonstration directory where the HTML pages are stored. |
| `return_str` | `bool` | `True` | If True, returns the path as a string, otherwise returns a Path object |
| `throw_error` | `bool` | `True` | If True, throws an error if the turn does not have an HTML page, otherwise returns None |


#### `Turn.get_bboxes_path`

```
weblinx.Turn.get_bboxes_path(self, subdir="bboxes", page_subdir="pages", throw_error=True)
```

##### Description

Returns the path to the bounding boxes file for the current turn. If the turn does not have bounding boxes
and `throw_error` is set to True, this function will raise a ValueError. Otherwise, it will return None.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `subdir` | `str` | `"bboxes"` | The subdirectory within the demonstration directory where bounding boxes are stored. Default is "bboxes". |
| `page_subdir` | `str` | `"pages"` | The subdirectory where page files are stored. Default is "pages". This parameter is currently not used in the function body and could be considered for removal or implementation. |
| `throw_error` | `bool` | `True` | Determines whether to throw an error if bounding boxes are not found. If False, returns None in such cases. |


##### Returns

```
Path or None
```

The path to the bounding box file as a pathlib.Path object if found, otherwise None.

#### `Turn.get_screenshot_status`

```
weblinx.Turn.get_screenshot_status(self)
```

##### Description

Retrieves the status of the screenshot associated with the turn. The status can be 'good', 'broken',
or None if the status is not defined, which might be the case for turns without a screenshot.


##### Returns

```
Optional[str]
```

A string indicating the screenshot status ('good', 'broken', or None).

#### `Turn.get_xpaths_dict`

```
weblinx.Turn.get_xpaths_dict(self, uid_key="data-webtasks-id", cache_dir=None, allow_save=True, check_hash=False, parser="lxml", json_backend="auto")
```

##### Description

Retrieves the XPaths for elements in the turn's HTML page that match a specified attribute name (uid_key).
If a cache directory is provided, it attempts to load cached XPaths before computing new ones. Newly computed
XPaths can be saved to the cache if `allow_save` is True. If `check_hash` is True, it validates the HTML hash
before using cached data.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `uid_key` | `str` | `"data-webtasks-id"` | The attribute name to match elements by in the HTML document. |
| `cache_dir` | `str or Path` | `None` | The directory where XPaths are cached. If None, caching is disabled. |
| `allow_save` | `bool` | `True` | Whether to save newly computed XPaths to the cache directory. |
| `check_hash` | `bool` | `False` | Whether to validate the HTML hash before using cached XPaths. |
| `parser` | `str` | `"lxml"` | The parser backend to use for HTML parsing. Currently, only 'lxml' is supported. |
| `json_backend` | `str` | `"auto"` | The backend to use for loading and saving JSON. If 'auto', chooses the best available option. |


##### Returns

```
dict
```

A dictionary mapping unique IDs (from `uid_key`) to their corresponding XPaths in the HTML document.

### `Replay`

```
weblinx.Replay(replay_json, demo_name, base_dir)
```

#### Description

Represents a replay of a demonstration, encapsulating a sequence of turns (actions and states) within a web session.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `replay_json` | `dict` |  | The JSON object containing the replay data. |
| `demo_name` | `str` |  | The name of the demonstration this replay belongs to. |
| `base_dir` | `str` |  | The base directory where the demonstration data is stored. |


#### `Replay.__getitem__`

```
weblinx.Replay.__getitem__(self, key)
```

#### `Replay.__len__`

```
weblinx.Replay.__len__(self)
```

#### `Replay.__repr__`

```
weblinx.Replay.__repr__(self)
```

#### `Replay.__iter__`

```
weblinx.Replay.__iter__(self)
```

#### `Replay.from_demonstration`

```
weblinx.Replay.from_demonstration(cls, demonstration)
```

##### Description

Returns a Replay object from a demonstration object.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `demonstration` | `Demonstration` |  | Demonstration object to create the replay from. It will use the replay.json file in the demonstration directory, as well as the name and base directory of the demonstration. |


#### `Replay.num_turns`

```
weblinx.Replay.num_turns(self)
```

#### `Replay.filter_turns`

```
weblinx.Replay.filter_turns(self, turn_filter)
```

##### Description

Filter the turns in the replay by a custom filter function that takes as input a turn object
and returns a list of Turn objects that satisfy the filter function.

#### `Replay.filter_by_type`

```
weblinx.Replay.filter_by_type(self, turn_type)
```

##### Description

Filters the turns in the replay based on their type ('browser' or 'chat').


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn_type` | `str` |  | The type of turns to filter by. Must be either 'browser' or 'chat'. |


##### Returns

```
List[Turn]
```

A list of Turn objects that match the specified type.

#### `Replay.filter_by_intent`

```
weblinx.Replay.filter_by_intent(self, intent)
```

##### Description

Filter the turns in the replay by action intent

#### `Replay.filter_by_intents`

```
weblinx.Replay.filter_by_intents(self, intents)
```

##### Description

Filter the turns in the replay by a list of action intents.

You can either pass a list of intents as the first argument, or pass the intents as
separate arguments. For example, the following two calls are equivalent:

```
replay.filter_by_intents(['click', 'scroll'])
replay.filter_by_intents('click', 'scroll')
```

#### `Replay.validate_turns`

```
weblinx.Replay.validate_turns(self)
```

##### Description

Validate all turns in the replay. If any turn is invalid, it will return False.
If all turns are valid, it will return True. Check `Turn.validate` for more information.

#### `Replay.filter_if_screenshot`

```
weblinx.Replay.filter_if_screenshot(self)
```

##### Description

Filter the turns in the replay by whether the turn contains a screenshot

#### `Replay.filter_if_html_page`

```
weblinx.Replay.filter_if_html_page(self)
```

##### Description

Filter the turns in the replay by whether the turn contains an HTML page

#### `Replay.list_types`

```
weblinx.Replay.list_types(self)
```

##### Description

List all turn types in the current replay (may not be exhaustive)

#### `Replay.list_intents`

```
weblinx.Replay.list_intents(self)
```

##### Description

List all action intents in the current replay (may not be exhaustive)

#### `Replay.list_screenshots`

```
weblinx.Replay.list_screenshots(self, return_str=True)
```

##### Description

List path of all screenshots in the current replay (may not be exhaustive).
If return_str is True, return the screenshot paths as strings instead of Path objects.


##### Note

If you want to list all screenshots available for a demonstration (even ones
that are not in the replay), use the `list_screenshots` method of the Demonstration class.

#### `Replay.list_html_pages`

```
weblinx.Replay.list_html_pages(self, return_str=True)
```

##### Description

List path of all HTML pages in the current replay (may not be exhaustive)

#### `Replay.list_urls`

```
weblinx.Replay.list_urls(self)
```

##### Description

List all URLs in the current replay (may not be exhaustive)

#### `Replay.assign_screenshot_to_turn`

```
weblinx.Replay.assign_screenshot_to_turn(self, turn, method="previous_turn")
```

##### Description

Sets the screenshot path of a turn. This will set the screenshot path
under the state -> screenshot key of the turn. If the turn already has a
screenshot path, it will be overwritten. If no possible screenshot path
can be determined, it will return None, else it will return the screenshot
path.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | Turn object to set the screenshot path for. This will modify the turn in-place. |
| `method` | `str` | `"previous_turn"` | Method to use to set the screenshot path. If 'previous_turn', it will use the index of  the last turn in the demonstration to determine the screenshot path. At the moment, this is the only method available. |


#### `Replay.assign_html_path_to_turn`

```
weblinx.Replay.assign_html_path_to_turn(self, turn, method="previous_turn")
```

##### Description

Sets the HTML path of a turn. This will set the HTML path
under the state -> page key of the turn. If the turn already has an
HTML path, it will be overwritten. If no possible HTML path
can be determined, it will return None, else it will return the HTML
path.


##### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn` | `Turn` |  | Turn object to set the HTML path for. This will modify the turn in-place. |
| `method` | `str` | `"previous_turn"` | Method to use to set the HTML path. If 'previous_turn', it will use the index of  the last turn in the demonstration to determine the HTML path. At the moment, this is the only method available. |


### `list_demonstrations`

```
weblinx.list_demonstrations(base_dir="./demonstrations", valid_only=False)
```

#### Description

List all demonstrations in the base directory, returning a list of Demo objects.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `base_dir` | `str` | `"./demonstrations"` | Base directory containing all demonstrations |
| `valid_only` | `bool` | `False` | Whether to only return valid demonstrations. This will call `Demonstration.is_valid` with the default parameters. |


### `filter_turns`

```
weblinx.filter_turns(turns, turn_filter)
```

#### Description

Filter a list of turns using a custom filter function. This is similar
to Replay.filter_turns, but it can be used with any list of turns, instead
of only with a Replay object.

### `load_demos_in_split`

```
weblinx.load_demos_in_split(split_path, split="train", sample_size=None, random_state=42, demo_base_dir="./demonstrations")
```

#### Description

Loads demos from a json file containing many splits. The json file should be a dictionary with
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
demos
```

A list of Demonstration objects corresponding to the demos in the split.

#### Note

This function uses webtasks.utils.load_demo_names_in_split behind the scenes,
then apply wt.Demonstration to each demo name.

