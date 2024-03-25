import datetime as dt
from functools import cached_property, lru_cache
import hashlib
from pathlib import Path
import json
from typing import Callable, Iterator, List, Union
import importlib

from .version import __version__
from . import utils


def format_repr(cls, *attributes, **kwargs):
    """
    Generate a __repr__ method for a class with the given attributes
    """
    attrs = [f"{attr}={getattr(cls, attr)}" for attr in attributes]
    attrs += [f"{key}={value}" for key, value in kwargs.items()]
    return f'{cls.__class__.__name__}({", ".join(attrs)})'


def _validate_json_backend(backend):
    if backend not in ["auto", "json", "orjson", "ujson"]:
        raise ValueError(
            f"Invalid backend '{backend}'. Must be either 'auto', 'json', 'ujson', or 'orjson'"
        )

    for candidate_backend in ["orjson", "ujson"]:
        spec = importlib.util.find_spec(candidate_backend)
        if backend == candidate_backend and spec is None:
            # Check if it exists with importlib
            raise ImportError(
                f"{candidate_backend} is not installed. Please change your "
                f"json backend or install it with `pip install {candidate_backend}`"
            )


class Demonstration:
    def __init__(self, name, base_dir="./demonstrations", json_backend="auto", encoding=None):
        """
        Parameters
        ----------
        name: str
            Name of the demonstration directory

        base_dir: str
            Base directory containing all demonstrations directories

        json_backend: str
            Backend to use to load JSON files. Can be either 'auto', 'json',
            'orjson', or 'ujson'. For the 'auto' option, it will try to import
            'orjson' first, then 'ujson', then 'json'. Both 'orjson' and 'ujson'
            are faster than 'json', but they must be installed first, via
            `pip install orjson` or `pip install ujson`.
        
        encoding: str
            Encoding to use when reading and writing files. If None, it will use the system's default encoding.
        """
        _validate_json_backend(json_backend)

        self.name = name
        self.base_dir = base_dir
        self.json_backend = json_backend
        self.path = Path(base_dir, name)
        self.jsons = {}
        self.encoding = encoding

    def __repr__(self):
        return format_repr(self, "name", "base_dir")

    @cached_property
    def metadata(self) -> dict:
        """
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
        """
        return self.load_json("metadata.json")

    @cached_property
    def replay(self) -> dict:
        """
        Returns the replay dictionary with two keys:
            - data: list of data points
            - version: version of the demonstration

        Note
        ----
        If you want a `Replay` object, call `Replay.from_demonstration(demo)`.
        """
        return self.load_json("replay.json")

    @cached_property
    def form(self) -> dict:
        """
        Returns the form dictionary, which contains the form dictionary with the following keys:
            - annotator: name of the annotator
            - description: description of the demonstration
            - tasks: list of tasks
            - navigator_name: name of the navigator
            - instructor_name: name of the instructor
            - shortcode: randomly generated unique shortcode to identify the demonstration
            - upload_date: date when the demonstration was uploaded
        """
        return self.load_json("form.json")

    def has_file(self, filename) -> bool:
        """
        Check if a file exists in the demonstration directory
        """
        return Path(self.path, filename).exists()

    def is_valid(self, check_invalid_file=True) -> bool:
        """
        Verifies that the demonstration directory is valid by
        checking that all required files exist.

        Parameters
        ----------
        check_invalid_file: bool
            Whether to check if the demonstration has an invalid.json file.
        """
        required_files = ["metadata.json", "replay.json", "form.json"]
        has_correct_files = all(
            [self.has_file(filename) for filename in required_files]
        )

        if not check_invalid_file:
            return has_correct_files
        else:
            return has_correct_files and not self.has_file("invalid.json")

    def load_json(self, filename, backend=None, default=None, encoding=None) -> dict:
        """
        Load a JSON file from the demonstration directory

        Parameters
        ----------
        filename: str
            Name of the file to load

        backend: str
            Backend to use to load the JSON file. Can be either None, 'auto',
            'json', 'orjson', or 'ujson'. If 'auto', it will try to import
            'orjson' first, then 'ujson', then 'json'. If None, it will use
            the json_backend specified in the constructor.

        default: Any
            Default value to return if the file does not exist. If None, it will raise an error.
        
        encoding: str
            Encoding to use when reading the file. If None, it will default to the Demonstration's encoding
            specified in the constructor, or the system's default encoding if it was not specified.
        """
        if encoding is None:
            encoding = self.encoding
        
        if not self.has_file(filename):
            if default is not None:
                return default

            raise FileNotFoundError(f"File '{filename}' not found in '{self.path}'")

        if backend is None:
            backend = self.json_backend

        _validate_json_backend(backend)

        results = utils.auto_read_json(self.path / filename, backend=backend, encoding=encoding)

        return results

    def save_json(
        self, obj: Union[str, dict], filename: str, overwrite=False, indent=2
    ) -> str:
        """
        Saves an object to the demonstration directory. If it's a string,
        it will be saved as-is. If it's a dictionary, it will be saved as
        a JSON file.

        Parameters
        ----------
        obj: Union[str, dict]
            Object to save. If it's a string, it will be saved as-is. If it's a dictionary,
            it will be saved as a JSON file.

        filename: str
            Name of the file to save the object to.

        overwrite: bool
            Whether to overwrite the file if it already exists. If False, the file will not
            be overwritten and the function will return the path to the existing file.
        """
        if isinstance(obj, dict):
            obj = json.dumps(obj, indent=indent)

        path = self.path / filename

        if path.exists() and not overwrite:
            return str(path)

        with open(path, "w") as f:
            f.write(obj)

        return str(path)

    def get_version(self, as_tuple=True) -> Union[str, tuple]:
        """
        Returns the version of the demonstration as a string or tuple
        """
        version = self.metadata["version"]

        if as_tuple:
            return tuple(map(int, version.split(".")))
        else:
            return version

    def get_recording_path(
        self, format="mp4", prefix="video", return_str=True
    ) -> Union[Path, str]:
        """
        Returns the path to the recording file

        format: format of the recording file
        prefix: prefix of the recording file
        return_str: whether to return a string instead of a Path object
        """
        pattern = f"{prefix}*.{format}"
        paths = list(self.path.glob(pattern))
        if len(paths) == 0:
            raise FileNotFoundError(f"Recording file not found in '{self.path}'")

        return str(paths[0]) if return_str else paths[0]

    def get_screenshot_path(self, name, return_str=True) -> Union[Path, str]:
        """
        Returns the path to the screenshot file

        index: index of the screenshot
        return_str: whether to return a string instead of a Path object
        """
        path = self.path / "screenshots" / name
        if not path.exists():
            raise FileNotFoundError(f"Screenshot file not found in '{path}'")

        return str(path) if return_str else path

    def get_upload_date(self, as_datetime=False) -> Union[str, dt.datetime]:
        """
        Returns the upload date of the demonstration as a string or datetime object
        """
        upload_date = self.form["upload_date"]

        if as_datetime:
            return dt.datetime.strptime(upload_date, "%Y-%m-%d %H:%M:%S")
        else:
            return upload_date

    def list_all_screenshots(self, return_str=True) -> List[Union[str, Path]]:
        """
        Returns a list of all screenshots (including ones not in the replay)
        """
        globbed = self.path.joinpath("screenshots").glob("screenshot-*.png")
        sorted_paths = list(sorted(globbed, key=utils.rank_paths))

        if return_str:
            sorted_paths = [str(path) for path in sorted_paths]

        return sorted_paths

    def list_all_html_pages(self, return_str=True) -> List[Union[str, Path]]:
        """
        Returns a list of all HTML files (including ones not in the replay)
        """
        globbed = self.path.joinpath("pages").glob("page-*.html")

        sorted_paths = list(sorted(globbed, key=utils.rank_paths))

        if return_str:
            sorted_paths = [str(path) for path in sorted_paths]

        return sorted_paths

    def join(self, *args) -> Path:
        """
        Joins the demonstration path with the given arguments.

        Example
        -------
        ```
        demo = wt.Demonstration('...')

        html_path = demo.join('pages', 'page-1-0.html')
        ```
        """
        return self.path.joinpath(*args)


class Turn(dict):
    def __init__(
        self,
        turn_dict: dict,
        index: int,
        demo_name: str,
        base_dir: str,
        json_backend="auto",
        encoding=None,
    ):
        """
        This class represents a turn in a demonstration, and can be used as a dictionary.
        """
        super().__init__(turn_dict)
        self.index = index
        self.demo_name = demo_name
        self.base_dir = base_dir
        self.json_backend = json_backend
        self.encoding = encoding

        _validate_json_backend(json_backend)

    def __repr__(self):
        return format_repr(self, "index", "demo_name", "base_dir")

    @classmethod
    def from_replay(cls, replay: "Replay", index: int):
        """
        Returns a Turn object from a replay and an index
        """
        return cls(
            turn_dict=replay[index],
            index=index,
            demo_name=replay.demo_name,
            base_dir=replay.base_dir,
            encoding=replay.encoding,
        )

    @property
    def args(self) -> dict:
        """
        Arguments of the turn. This is a shortcut to access the arguments
        of the action, which is nested under action -> arguments. It
        returns None if the turn is not a browser turn.
        """
        action = self.get("action", {})
        if action is None:
            return None

        return action.get("arguments")

    @property
    def type(self) -> str:
        """
        Type of the turn, either 'browser' or 'extension'
        """
        return self["type"]

    @property
    def timestamp(self) -> float:
        """
        Number of seconds since the start of the demonstration
        """
        return self["timestamp"]

    @property
    def intent(self) -> str:
        """
        If the turn is a browser turn, returns the intent of the action, otherwise returns None
        """
        action = self.get("action", {})
        if action is None:
            return None

        return action.get("intent")

    @property
    def metadata(self) -> dict:
        """
        If the turn is a browser turn, returns the metadata of the action, otherwise returns None

        Note
        ----
        The metadata is nested under action -> arguments -> metadata, so this property
        is a shortcut to access it.
        """
        args = self.args

        if args is None:
            return None

        return args.get("metadata")

    @property
    def url(self) -> str:
        """
        If the turn is a browser turn, returns the URL of the action, otherwise returns None

        Note
        ----
        The URL is nested under action -> arguments -> metadata -> url, so this property
        is a shortcut to access it.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("url")

    @property
    def tab_id(self) -> int:
        """
        If the turn is a browser turn, returns the tab ID of the action, otherwise returns `None`.
        The tab ID is an integer that uniquely identifies a tab in the browser. If tab_id == -1,
        then it means there was no tab ID associated with the action (e.g. if the action was to
        delete a tab); in contrast, `tab_id` being `None` means that the turn did not have a
        action metadata.

        Note
        ----
        The tab ID is nested under action -> arguments -> metadata -> tabId, so this property
        is a shortcut to access it.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("tabId")

    @property
    def viewport_height(self) -> int:
        """
        If the turn is a browser turn, returns the viewport height of the action, otherwise returns `None`.
        The viewport height is an integer that represents the height of the viewport in the browser.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("viewportHeight")

    @property
    def viewport_width(self) -> int:
        """
        If the turn is a browser turn, returns the viewport width of the action, otherwise returns `None`.
        The viewport width is an integer that represents the width of the viewport in the browser.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("viewportWidth")

    @property
    def mouse_x(self) -> int:
        """
        If the turn is a browser turn, returns the mouse X position of the action, otherwise returns `None`.
        The mouse X position is an integer that represents the X position of the mouse in the browser.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("mouseX")

    @property
    def mouse_y(self) -> int:
        """
        If the turn is a browser turn, returns the mouse Y position of the action, otherwise returns `None`.
        The mouse Y position is an integer that represents the Y position of the mouse in the browser.
        """
        if self.metadata is None:
            return None

        return self.metadata.get("mouseY")

    @property
    def client_x(self) -> int:
        """
        If the turn is a browser turn, returns the client X position of the action, otherwise returns `None`.
        The client X is the mouse X position scaled with zoom.
        """
        if self.props is None:
            return None

        return self.props.get("clientX")

    @property
    def client_y(self) -> int:
        """
        If the turn is a browser turn, returns the client Y position of the action, otherwise returns `None`.
        The client Y is the mouse Y position scaled with zoom.
        """
        if self.props is None:
            return None

        return self.props.get("clientY")

    @property
    def zoom(self) -> float:
        """
        If the turn is a browser turn, returns the zoom level of the action, otherwise returns `None`.
        The zoom level is a float that represents how much the page is zoomed in or out.
        """

        if self.metadata is not None and "zoomLevel" in self.metadata:
            return float(self.metadata["zoomLevel"])
        else:
            return None

    @property
    def element(self) -> dict:
        """
        If the turn is a browser turn, returns the element of the action, otherwise returns None

        Example
        -------

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
            "outerHTML": "<button width=\"100%\" ...>Search</button>",
            "tagName": "BUTTON",
            "textContent": "Search",
            "xpath": "id(\"root\")/main[1]/.../button[1]"
        }
        ```


        Note
        ----
        The element is nested under action -> arguments -> element, so this property
        is a shortcut to access it.
        """
        args = self.args
        if args is None:
            return None

        return args.get("element")

    @property
    def props(self) -> dict:
        """
        If the turn is a browser turn, returns the properties of the action, otherwise returns None.

        Example
        -------

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

        Note
        ----
        The props is nested under action -> arguments -> properties, so this property
        is a shortcut to access it.
        """
        args = self.args
        if args is None:
            return None

        return args.get("properties")

    @cached_property
    def bboxes(self) -> dict:
        """
        This uses the path returned by `self.get_bboxes_path()` to load the bounding boxes of the turn,
        and parse them with JSON to return a dictionary, or return None if the path is invalid. It relies
        on the default parameters of `self.get_bboxes_path()` to get the path to the bounding boxes.

        Note
        ----
        If you want to change the default parameters, you can call `self.get_bboxes_path()` with the
        desired parameters and then load the JSON file yourself:

        ```
        import json

        turns = wt.Replay.from_demonstrations(demo).filter_if_html_page()

        path = turns[0].get_bboxes_path(subdir="bboxes", page_subdir="pages")

        with open(path) as f:
            bboxes = json.load(f)
        ```
        """
        path = self.get_bboxes_path(throw_error=False)
        if path is None:
            return None

        bboxes = utils.auto_read_json(path, backend=self.json_backend, encoding=self.encoding)

        return bboxes

    @cached_property
    def html(self) -> str:
        """
        This uses the path returned by `self.get_html_path()` to load the HTML of the turn,
        and return it as a string, or return None if the path is invalid. It relies on the
        default parameters of `self.get_html_path()` to get the path to the HTML page.

        Example
        --------
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
        """
        if not self.has_html():
            return None

        return utils.html.open_html_with_encodings(
            self.get_html_path(), raise_error=False
        )

    def format_text(self, max_length=50) -> str:
        """
        This returns a string representation of the action or utterance. In the case of action
        we have a combination of the tag name, text content, and intent, with the format:
        `[tag] text -> INTENT: arg`.

        If it is a chat turn, we have a combination of the speaker and utterance, with the format:
        `[say] utterance -> SPEAKER`.

        Example
        --------

        If the action is a click on a button with the text "Click here", the output will be:
        ```
        [button] Click here -> CLICK
        ```

        If the action is to input the word "world" in a text input that already has the word "Hello":
        ```
        [input] Hello -> TEXTINPUT: world
        ```
        """
        if self.type == "chat":
            speaker = self.get("speaker").lower()
            utterance = self.get("utterance").strip()

            return f"[{speaker.lower()}] -> SAY: {utterance}"

        s = ""
        if self.element is not None:
            # else, it's a browser turn
            tag = self.element["tagName"].lower().strip()
            text = self.element["textContent"].strip()
            # Remove leading \n and trailing \n
            text = text.strip("\n")
            text = utils.shorten_text(text, max_length=max_length)

            s += f"[{tag}] {text}"

        s += f" -> {self.intent.upper()}"

        # If intent has a value, append it to the string
        if (args := self.args) is None:
            return s

        data = None

        if self.intent == "textInput":
            data = args.get("text")
        elif self.intent == "change":
            data = args.get("value")
        elif self.intent == "scroll":
            data = f'x={args["scrollX"]}, y={args["scrollY"]}'
        elif self.intent == "say":
            data = args.get("text")
        elif self.intent == "copy":
            data = utils.shorten_text(args.get("selected"), max_length=max_length)
        elif self.intent == "paste":
            data = utils.shorten_text(args.get("pasted"), max_length=max_length)
        elif self.intent in ["tabcreate", "tabremove"]:
            data = args.get("properties", {}).get("tabId")
        elif self.intent == "tabswitch":
            data = f'from={args["properties"]["tabIdOrigin"]}, to={args["properties"]["tabId"]}'
        elif self.intent == "load":
            url = args["properties"].get("url") or args.get("url", "")
            data = utils.url.shorten_url(url, width=max_length)

            if args["properties"].get("transitionType"):
                quals = " ".join(args["properties"]["transitionQualifiers"])
                data += f', transition={args["properties"]["transitionType"]}'
                data += f", qualifiers=({quals})"

        if data is not None:
            s += f": {data}"

        return s

    def validate(self) -> bool:
        """
        This checks if the following keys are present:
        - type
        - timestamp

        Additionally, it must have one of the following combinations:
        - action, state
        - speaker, utterance
        """
        required_keys = ["type", "timestamp"]
        if not all([key in self for key in required_keys]):
            return False

        if self.type == "browser":
            required_keys = ["action", "state"]

        elif self.type == "chat":
            required_keys = ["speaker", "utterance"]

        else:
            return False

        return all([key in self for key in required_keys])

    def has_screenshot(self):
        """
        Returns True if the turn has a screenshot, False otherwise
        """
        return self.get("state", {}).get("screenshot") is not None

    def has_html(self):
        """
        Returns True if the turn has an associated HTML page, False otherwise
        """
        state = self.get("state")
        if state is None:
            return False

        return state.get("page") is not None

    def has_bboxes(self, subdir: str = "bboxes", page_subdir: str = "pages"):
        """
        Checks if the turn has bounding boxes
        """
        return (
            self.get_bboxes_path(
                subdir=subdir, page_subdir=page_subdir, throw_error=False
            )
            is not None
        )

    def get_screenshot_path(
        self,
        subdir: str = "screenshots",
        return_str: bool = True,
        throw_error: bool = True,
    ) -> Union[Path, str]:
        """
        Returns the path to the screenshot of the turn, throws an error if the turn does not have a screenshot

        Parameters
        ----------
        subdir: str
            Subdirectory of the demonstration directory where the HTML pages are stored.

        return_str: bool
            If True, returns the path as a string, otherwise returns a Path object

        throw_error: bool
            If True, throws an error if the turn does not have an HTML page, otherwise returns None
        """
        if not self.has_screenshot():
            if throw_error:
                raise ValueError(f"Turn {self.index} does not have a screenshot")
            else:
                return None

        path = Path(self.base_dir, self.demo_name, subdir, self["state"]["screenshot"])

        if return_str:
            return str(path)
        else:
            return path

    def get_html_path(
        self, subdir: str = "pages", return_str: bool = True, throw_error: bool = True
    ) -> Union[Path, str]:
        """
        Returns the path to the HTML page of the turn.

        Parameters
        ----------
        subdir: str
            Subdirectory of the demonstration directory where the HTML pages are stored.

        return_str: bool
            If True, returns the path as a string, otherwise returns a Path object

        throw_error: bool
            If True, throws an error if the turn does not have an HTML page, otherwise returns None
        """
        if not self.has_html():
            if throw_error:
                raise ValueError(f"Turn {self.index} does not have an HTML page")
            else:
                return None

        path = Path(self.base_dir, self.demo_name, subdir, self["state"]["page"])

        if return_str:
            return str(path)
        else:
            return path

    def get_bboxes_path(
        self, subdir="bboxes", page_subdir="pages", throw_error: bool = True
    ) -> List[dict]:
        """
        Returns the path to the bounding boxes file for the current turn. If the turn does not have bounding boxes
        and `throw_error` is set to True, this function will raise a ValueError. Otherwise, it will return None.

        Parameters
        ----------
        subdir : str
            The subdirectory within the demonstration directory where bounding boxes are stored. Default is "bboxes".
        page_subdir : str
            The subdirectory where page files are stored. Default is "pages". This parameter is currently not used in the function body and could be considered for removal or implementation.
        throw_error : bool
            Determines whether to throw an error if bounding boxes are not found. If False, returns None in such cases.

        Returns
        -------
        Path or None
            The path to the bounding box file as a pathlib.Path object if found, otherwise None.
        """
        if not self.has_html():
            if throw_error:
                raise ValueError(
                    f"Turn {self.index} does not have an HTML page, so it does not have bounding boxes."
                )
            else:
                return None

        html_fname = self["state"]["page"]
        index, _ = utils.get_nums_from_path(html_fname)  # different from self.index!

        path = Path(self.base_dir, self.demo_name, subdir, f"bboxes-{index}.json")

        if not path.exists():
            if throw_error:
                raise ValueError(f"Turn {self.index} does not have bounding boxes")
            else:
                return None

        return path

    def get_screenshot_status(self):
        """
        Retrieves the status of the screenshot associated with the turn. The status can be 'good', 'broken',
        or None if the status is not defined, which might be the case for turns without a screenshot.

        Returns
        -------
        Optional[str]
            A string indicating the screenshot status ('good', 'broken', or None).
        """
        return self["state"].get("screenshot_status")

    def get_xpaths_dict(
        self,
        uid_key="data-webtasks-id",
        cache_dir=None,
        allow_save=True,
        check_hash=False,
        parser="lxml",
        json_backend="auto",
        encoding=None,
    ):
        """
        Retrieves the XPaths for elements in the turn's HTML page that match a specified attribute name (uid_key).
        If a cache directory is provided, it attempts to load cached XPaths before computing new ones. Newly computed
        XPaths can be saved to the cache if `allow_save` is True. If `check_hash` is True, it validates the HTML hash
        before using cached data.

        Parameters
        ----------
        uid_key : str
            The attribute name to match elements by in the HTML document.
        cache_dir : str or Path, optional
            The directory where XPaths are cached. If None, caching is disabled.
        allow_save : bool
            Whether to save newly computed XPaths to the cache directory.
        check_hash : bool
            Whether to validate the HTML hash before using cached XPaths.
        parser : str
            The parser backend to use for HTML parsing. Currently, only 'lxml' is supported.
        json_backend : str
            The backend to use for loading and saving JSON. If 'auto', chooses the best available option.
        encoding: str
            Encoding to use when reading the file. If None, it will default to the Demonstration's encoding
            specified in the constructor, or the system's default encoding if it was not specified.
        
        Returns
        -------
        dict
            A dictionary mapping unique IDs (from `uid_key`) to their corresponding XPaths in the HTML document.
        """
        if encoding is None:
            encoding = self.encoding
        
        if parser != "lxml":
            raise ValueError(f"Invalid backend '{parser}'. Must be 'lxml'.")

        if cache_dir is not None:
            cache_dir = Path(cache_dir, self.demo_name)
            cache_path = cache_dir / f"xpaths-{self.index}.json"
            if cache_path.exists():
                result = utils.auto_read_json(cache_path, backend=json_backend, encoding=encoding)
                # If the hash is different, then the HTML has changed, so we need to
                # recompute the XPaths
                if not check_hash:
                    return result["xpaths"]

                elif (
                    check_hash
                    and result["md5"] == hashlib.md5(self.html.encode()).hexdigest()
                ):
                    return result["xpaths"]

        try:
            import lxml.html
        except ImportError:
            raise ImportError(
                "The lxml package is required to use this function. Install it with `pip install lxml`."
            )

        html = self.html
        if html is None:
            return {}

        tree = lxml.html.fromstring(html).getroottree()

        elems = tree.xpath(f"//*[@{uid_key}]")
        if len(elems) == 0:
            return {}

        xpaths = {}

        for elem in elems:
            uid = elem.attrib[uid_key]
            xpath = tree.getpath(elem)
            xpaths[uid] = xpath

        if cache_dir is not None and allow_save:
            cache_dir.mkdir(parents=True, exist_ok=True)
            save_file = {
                "xpaths": xpaths,
                "md5": hashlib.md5(html.encode()).hexdigest(),
            }
            utils.auto_save_json(save_file, cache_path, backend=json_backend)

        return xpaths


class Replay:
    """
    A replay is one of the core components of a demonstration. It is a list of turns, each of
    which contains the information about the state of the browser, the action that was performed,
    and the HTML element that was interacted. It also has information about the action that was
    performed at each turn, and the timestamp of the action. If the type of turn is a 'chat' turn,
    then it will contain information about what was said in the chat.
    """

    def __init__(self, replay_json: dict, demo_name: str, base_dir: str, encoding=None):
        """
        Represents a replay of a demonstration, encapsulating a sequence of turns (actions and states) within a web session.

        Parameters
        ----------
        replay_json : dict
            The JSON object containing the replay data.
        demo_name : str
            The name of the demonstration this replay belongs to.
        base_dir : str
            The base directory where the demonstration data is stored.
        encoding : str
            The encoding to use when reading files. If None, it will default to the system's default encoding.
        """
        self.data_dict = replay_json["data"]
        self.demo_name = demo_name
        self.base_dir = str(base_dir)
        self.encoding = encoding

        created = replay_json.get("created", None)
        # TODO: check if this is the correct timestamp
        if created is not None:
            self.created = dt.datetime.fromtimestamp(created)
        else:
            self.created = None

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(len(self)))]

        if key < 0:
            key = len(self) + key

        elif key > len(self) - 1:
            raise IndexError(
                f"Turn index {key} out of range. The replay has {len(self)} turns, so the last index is {len(self) - 1}."
            )

        return Turn(
            self.data_dict[key],
            index=key,
            demo_name=self.demo_name,
            base_dir=self.base_dir,
            encoding=self.encoding,
        )

    def __len__(self):
        return len(self.data_dict)

    def __repr__(self):
        if self.created is not None:
            created = self.created.replace(microsecond=0)
        else:
            created = "unknown"
        return format_repr(
            self,
            "num_turns",
            created=created,
            demo_name=self.demo_name,
            base_dir=self.base_dir,
        )

    def __iter__(self) -> Iterator[Turn]:
        return iter(
            Turn(turn, index=i, demo_name=self.demo_name, base_dir=self.base_dir)
            for i, turn in enumerate(self.data_dict)
        )

    @classmethod
    def from_demonstration(cls, demonstration: Demonstration):
        """
        Returns a Replay object from a demonstration object.

        Parameters
        ----------
        demonstration: Demonstration
            Demonstration object to create the replay from. It will use the replay.json file
            in the demonstration directory, as well as the name and base directory of the
            demonstration.
        """
        replay = demonstration.replay
        return cls(
            replay,
            demo_name=demonstration.name,
            base_dir=demonstration.base_dir,
            encoding=demonstration.encoding,
        )

    @property
    def num_turns(self):
        return len(self)

    def filter_turns(self, turn_filter: Callable[[Turn], bool]) -> List[Turn]:
        """
        Filter the turns in the replay by a custom filter function that takes as input a turn object
        and returns a list of Turn objects that satisfy the filter function.
        """

        return [turn for turn in self if turn_filter(turn)]

    def filter_by_type(self, turn_type: str) -> List[Turn]:
        """
        Filters the turns in the replay based on their type ('browser' or 'chat').

        Parameters
        ----------
        turn_type : str
            The type of turns to filter by. Must be either 'browser' or 'chat'.

        Returns
        -------
        List[Turn]
            A list of Turn objects that match the specified type.
        """
        valid_types = ["browser", "chat"]
        if turn_type not in valid_types:
            raise ValueError(
                f"Invalid turn type: {turn_type}. Please choose one of: {valid_types}"
            )

        return self.filter_turns(lambda turn: turn.type == turn_type)

    def filter_by_intent(self, intent: str) -> List[Turn]:
        """
        Filter the turns in the replay by action intent
        """
        if intent == "say":
            return self.filter_turns(lambda turn: turn.type == "chat")
        else:
            return self.filter_turns(lambda turn: turn.intent == intent)

    def filter_by_intents(self, intents: List[str], *args) -> List[Turn]:
        """
        Filter the turns in the replay by a list of action intents.

        You can either pass a list of intents as the first argument, or pass the intents as
        separate arguments. For example, the following two calls are equivalent:

        ```
        replay.filter_by_intents(['click', 'scroll'])
        replay.filter_by_intents('click', 'scroll')
        ```
        """
        if not isinstance(intents, list):
            intents = [intents]

        if len(args) > 0:
            # merge the intents with the args
            intents = list(intents) + list(args)

        # Convert to set for faster lookup
        intents = set(intents)

        if "say" in intents:
            return self.filter_turns(
                lambda turn: turn.intent in intents or turn.type == "chat"
            )
        else:
            return self.filter_turns(lambda turn: turn.intent in intents)

    def validate_turns(self) -> List[bool]:
        """
        Validate all turns in the replay. If any turn is invalid, it will return False.
        If all turns are valid, it will return True. Check `Turn.validate` for more information.
        """
        return all([turn.validate() for turn in self])

    @lru_cache()
    def filter_if_screenshot(self) -> List[Turn]:
        """
        Filter the turns in the replay by whether the turn contains a screenshot
        """
        return self.filter_turns(lambda turn: turn.has_screenshot())

    def filter_if_html_page(self) -> List[Turn]:
        """
        Filter the turns in the replay by whether the turn contains an HTML page
        """
        return self.filter_turns(lambda turn: turn.has_html())

    @lru_cache()
    def list_types(self) -> List[str]:
        """
        List all turn types in the current replay (may not be exhaustive)
        """
        return list({turn.type for turn in self})

    @lru_cache()
    def list_intents(self):
        """
        List all action intents in the current replay (may not be exhaustive)
        """
        return list(set(turn.intent for turn in self))

    @lru_cache()
    def list_screenshots(self, return_str: bool = True):
        """
        List path of all screenshots in the current replay (may not be exhaustive).
        If return_str is True, return the screenshot paths as strings instead of Path objects.

        Note
        ----
        If you want to list all screenshots available for a demonstration (even ones
        that are not in the replay), use the `list_screenshots` method of the Demonstration class.
        """
        return [
            turn.get_screenshot_path(return_str=return_str)
            for turn in self
            if turn.has_screenshot()
        ]

    @lru_cache()
    def list_html_pages(self, return_str: bool = True):
        """
        List path of all HTML pages in the current replay (may not be exhaustive)
        """
        return [
            turn.get_html_path(return_str=return_str)
            for turn in self
            if turn.has_html()
        ]

    @lru_cache()
    def list_urls(self):
        """
        List all URLs in the current replay (may not be exhaustive)
        """
        return list(set(turn.url for turn in self if turn.url is not None))

    def assign_screenshot_to_turn(self, turn, method="previous_turn"):
        """
        Sets the screenshot path of a turn. This will set the screenshot path
        under the state -> screenshot key of the turn. If the turn already has a
        screenshot path, it will be overwritten. If no possible screenshot path
        can be determined, it will return None, else it will return the screenshot
        path.

        Parameters
        ----------

        turn: Turn
            Turn object to set the screenshot path for. This will modify the turn
            in-place.

        method: str
            Method to use to set the screenshot path. If 'previous_turn', it will use
            the index of  the last turn in the demonstration to determine the screenshot
            path. At the moment, this is the only method available.
        """

        if method not in ["previous_turn"]:
            raise ValueError(
                f"Invalid method '{method}'. Must be one of: 'previous_turn'"
            )

        if method == "previous_turn":
            index = turn.index - 1

            if index >= len(self) or index < 0:
                return None

            while index >= 0:
                prev_turn = self[index]

                if prev_turn.has_screenshot():
                    if "state" not in turn or turn["state"] is None:
                        turn["state"] = {}

                    turn["state"]["screenshot"] = prev_turn["state"]["screenshot"]
                    if "screenshot_status" in prev_turn["state"]:
                        turn["state"]["screenshot_status"] = prev_turn["state"][
                            "screenshot_status"
                        ]

                    return turn["state"]["screenshot"]

                index -= 1

            return None

    def assign_html_path_to_turn(self, turn, method="previous_turn"):
        """
        Sets the HTML path of a turn. This will set the HTML path
        under the state -> page key of the turn. If the turn already has an
        HTML path, it will be overwritten. If no possible HTML path
        can be determined, it will return None, else it will return the HTML
        path.

        Parameters
        ----------

        turn: Turn
            Turn object to set the HTML path for. This will modify the turn
            in-place.

        method: str
            Method to use to set the HTML path. If 'previous_turn', it will use
            the index of  the last turn in the demonstration to determine the HTML
            path. At the moment, this is the only method available.
        """

        if method not in ["previous_turn"]:
            raise ValueError(
                f"Invalid method '{method}'. Must be one of: 'previous_turn'"
            )

        if method == "previous_turn":
            index = turn.index - 1

            if index >= len(self) or index < 0:
                return None

            while index >= 0:
                prev_turn = self[index]

                if prev_turn.has_html():
                    if "state" not in turn or turn["state"] is None:
                        turn["state"] = {}

                    turn["state"]["page"] = prev_turn["state"]["page"]
                    return turn["state"]["page"]

                index -= 1

            return None


def list_demonstrations(
    base_dir: str = "./demonstrations", valid_only=False
) -> List[Demonstration]:
    """
    List all demonstrations in the base directory, returning a list of Demo objects.

    Parameters
    ----------
    base_dir: str
        Base directory containing all demonstrations

    valid_only: bool
        Whether to only return valid demonstrations. This will call `Demonstration.is_valid`
        with the default parameters.
    """
    path = Path(base_dir)
    demos = [
        Demonstration(demo.name, base_dir=base_dir)
        for demo in sorted(path.iterdir())
        if demo.is_dir()
    ]

    if valid_only:
        demos = [demo for demo in demos if demo.is_valid()]

    return demos


def filter_turns(turns: list, turn_filter: Callable[[Turn], bool]) -> list:
    """
    Filter a list of turns using a custom filter function. This is similar
    to Replay.filter_turns, but it can be used with any list of turns, instead
    of only with a Replay object.
    """
    return [turn for turn in turns if turn_filter(turn)]


def load_demos_in_split(
    split_path,
    split="train",
    sample_size=None,
    random_state=42,
    demo_base_dir="./demonstrations",
):
    """
    Loads demos from a json file containing many splits. The json file should be a dictionary with
    keys representing a split name (e.g. train, dev), and the values should be
    a list of demo names. This function will return the list of demo names
    corresponding to the split name.

    Parameters
    ----------
    split_path : str or Path
        The path to the json file containing all the splits.

    split : str
        The name of the split to load.

    sample_size : int
        If not None, then this function will return a random sample of the
        specified size.

    random_state : int
        The random state to use for sampling.

    Returns
    -------
    demos : list of Demonstration
        A list of Demonstration objects corresponding to the demos in the split.

    Note
    ----
    This function uses webtasks.utils.load_demo_names_in_split behind the scenes,
    then apply wt.Demonstration to each demo name.
    """

    return [
        Demonstration(demo_name, base_dir=demo_base_dir)
        for demo_name in utils.load_demo_names_in_split(
            split_path, split, sample_size, random_state
        )
    ]
