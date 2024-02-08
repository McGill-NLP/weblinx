"""
Contains 
"""

try:
    import cv2
    import numpy as np

except ImportError as e:
    raise ImportError(
        "OpenCV is not installed. To use this module, please install it with `pip install opencv-python-headless` or `pip install opencv-python`."
    )

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Union


from ..__init__ import Replay


@dataclass
class Viewport:
    h: int
    w: int

    @classmethod
    def from_metadata(cls, metadata: dict):
        """
        Returns a new Viewport from the metadata of a turn.
        """
        return cls(h=metadata["viewportHeight"], w=metadata["viewportWidth"])

    @classmethod
    def from_numpy(cls, array):  # h,w
        shape = array.shape
        return cls(h=shape[0], w=shape[1])

    @classmethod
    def from_pillow(cls, im):  # w,h
        return cls(h=im.height, w=im.width)

    @classmethod
    def from_cv2(cls, cap: "cv2.VideoCapture"):
        CAP_PROP_FRAME_WIDTH = 3
        CAP_PROP_FRAME_HEIGHT = 4

        w = int(cap.get(CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(CAP_PROP_FRAME_HEIGHT))

        return cls(h=h, w=w)

    @classmethod
    def from_video_path(cls, video_path: Union[str, Path]):
        video_path = str(video_path)

        cap = cv2.VideoCapture(video_path)
        obj = cls.from_cv2(cap)
        cap.release()

        return obj

    def scale(self, zoom_level: float):
        """
        Returns a new Viewport with the scaled height and width based on the zoom level.
        """
        z = float(zoom_level)
        return Viewport(h=int(round(self.h * z)), w=int(round(self.w * z)))


@dataclass
class CropArea:
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    def crop_numpy(self, array):
        """
        Crops a numpy array. based on the crop area (x_start, x_end, y_start, y_end)

        Note
        ----
        Numpy arrays of images have shape [h, w] (i.e. [row, column]), and the correspondance is
        w -> x and h -> y, so coordinates in an array are represented as [y, x].
        """
        return array[self.y_start : self.y_end, self.x_start : self.x_end]


def get_initial_viewport(replay: Replay) -> Viewport:
    # get initial viewport size and zoom level
    for turn in replay:
        if turn.metadata is not None:
            zoom_level = turn.metadata["zoomLevel"]
            view = Viewport.from_metadata(turn.metadata).scale(zoom_level)

            return view


def get_crop_area(full: Viewport, cropped: Viewport):
    """
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
    """
    y_start = full.h - cropped.h
    y_end = full.h

    x_start = 0
    x_end = cropped.w

    return CropArea(x_start=x_start, x_end=x_end, y_start=y_start, y_end=y_end)


def find_starting_frame(
    cap_or_path: Union[str, Path, cv2.VideoCapture],
    crop_area: CropArea = None,
    delay=5,
    min_redness=0.9,
    max_greenness=0.1,
    max_blueness=0.1,
    callback=None,
):
    """
    Given a video capture, start and end viewports, and a delay, find the index of the
    first frame that matches the criteria. The criteria is based on the average color
    of the frame. The delay is used to skip the first part of the video (before the
    extension is activated).

    Parameters
    ----------
    cap_or_path : str, Path, or cv2.VideoCapture
        If this is a string or a Path, we will create a new video capture object from
        that path. If it's a video capture object, we will use that object (but we
        will roll back the frame index to 0 and not close the object).

    crop_area : CropArea
        The area of the frame to crop. This is used to crop the frame before checking the
        average color. If `crop_area=None`, the whole frame will be used.

    delay : int
        The number of seconds to continue after the first red frame is found. This is because we
        want to use the LAST red frame, not the first one, and a delay allows us to wait
        until the last red frame is found.

    min_redness : float
        The minimum average redness of the frame. Higher values mean more red pixels. This
        is used to detect the frame with mostly red pixels.

    max_greenness : float
        The maximum average greenness of the frame. Lower values mean less green pixels. This
        is used to avoid frames that have a lot of pixels with a high average on the green
        channel (e.g. white screens).

    max_blueness : float
        The maximum average blueness of the frame. Lower values mean less blue pixels. This
        is used to avoid frames that have a lot of pixels with a high average on the blue
        channel (e.g. white screens).

    callback : callable
        A function that is called for each frame. It receives the index of the frame and the
        frame itself. It has the signature `callback(i: int, num_frames: int, frame: np.array)`.
        This is useful to track the progress of the function or to display the frame to the user.
        If  you can leave it as `None` if you don't need it.

    Returns
    -------
    int
        The index of the first frame that matches the criteria. You can access that frame via
        `cap.set(cv2.CAP_PROP_POS_FRAMES, idx)`.
    """
    if isinstance(cap_or_path, (str, Path)):
        cap = cv2.VideoCapture(str(cap_or_path))
        release_cap = True
    elif isinstance(cap_or_path, cv2.VideoCapture):
        cap = cap_or_path
        release_cap = False
    else:
        raise TypeError(
            f"Expected a string, Path, or cv2.VideoCapture, got {type(cap_or_path)}."
        )

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    fps = cap.get(cv2.CAP_PROP_FPS)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    countdown = fps * delay
    countdown_started = False

    red_idx = None

    for i in range(num_frames):
        ret, frame = cap.read()

        if not ret:
            if release_cap:
                cap.release()

            return None

        if callback is not None:
            callback(i, num_frames, frame)

        # We need to convert the frame from BGR to RGB.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # We crop the frame to the area of interest if a crop area is provided.
        if crop_area is not None:
            frame = crop_area.crop_numpy(frame)

        frame = frame / 255.0
        # Higher values mean more red pixels.
        redness = frame[:, :, 0].mean()
        # Lower values mean less green pixels.
        greenness = frame[:, :, 1].mean()
        # Lower values mean less blue pixels.
        blueness = frame[:, :, 2].mean()

        if (
            redness > min_redness
            and greenness < max_greenness
            and blueness < max_blueness
        ):
            red_idx = i
            countdown_started = True

        if countdown_started:
            countdown -= 1

        if countdown == 0:
            break

    if release_cap:
        cap.release()

    if red_idx is None:
        return None

    return red_idx + 1


def get_start_frame(
    demo,
    load_from_processed_metadata=True,
    save_to_processed_metadata=True,
    callback=None,
    delay=5,
):
    """
    This is a high-level function that wraps `find_starting_frame`, `get_initial_viewport`,
    and `get_crop_area` to find the starting frame of a demo. It also saves the starting
    frame to the processed metadata file of the demo, and can reload it from there if
    `load_from_processed_metadata=True`. This allows a concise way to get the starting
    frame of a demo (without having to wait for the expensive `find_starting_frame` to
    run every time).

    Parameters
    ----------
    demo : Demo
        The demo to get the starting frame of.

    load_from_processed_metadata : bool
        Whether to load the starting frame from the processed metadata file of the demo.
        This will read the processed_metadata.json file in the demo's path and return
        the value of the "start_frame" key if it exists. If it doesn't exist, it will
        run `find_starting_frame` and save the result to the processed metadata file.

    save_to_processed_metadata : bool
        Whether to save the starting frame to the processed metadata file of the demo.
        This will save the starting frame to the processed_metadata.json file in the
        demo's path.
    save_to_processed_metadata : bool
        Whether to save the starting frame to the processed metadata file of the demo.
        This will save the starting frame to the processed_metadata.json file in the
        demo's path.

    callback : callable
        A function that is called for each frame. It receives the index of the frame and the
        frame itself. It has the signature `callback(i: int, num_frames: int, frame: np.array)`.
        This is useful to track the progress of the function or to display the frame to the user.
        If  you can leave it as `None` if you don't need it.

    delay : int
        The number of seconds to continue after the first red frame is found. This is because we
        want to use the LAST red frame, not the first one, and a delay allows us to wait
        until the last red frame is found.

    Returns
    -------
    int
        The index of the starting frame of the demo.
    """
    from .. import Replay

    metadata_path = Path(demo.path) / "processed_metadata.json"
    if load_from_processed_metadata and metadata_path.exists():
        with open(metadata_path, "r") as fp:
            metadata = json.load(fp)
        if "start_frame" in metadata:
            return metadata["start_frame"]
    else:
        metadata = {}

    replay = Replay.from_demonstration(demo)
    rec_path = demo.get_recording_path()

    crop_area = get_crop_area(
        full=Viewport.from_video_path(rec_path),
        cropped=get_initial_viewport(replay),
    )

    start_frame = find_starting_frame(
        rec_path, crop_area=crop_area, callback=callback, delay=delay
    )

    if save_to_processed_metadata:
        metadata["start_frame"] = start_frame

        with open(metadata_path, "w") as fp:
            json.dump(metadata, fp, indent=2)

    return start_frame


def get_fps(video_path: str):
    """
    Given a video path, return the FPS of the video.

    Parameters
    ----------
    video_path : str
        The path to the video file.

    Returns
    -------
    float
        The FPS of the video.
    """
    if not isinstance(video_path, str):
        raise TypeError(f"Expected a string, got {type(video_path)}.")
    if not Path(video_path).exists():
        raise ValueError(f"File {video_path} does not exist.")

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps


def get_frame(video_path: str, frame_number: int) -> np.array:
    """
    Given a video_path and a frame number, return the frame.
    Behind the scenes, this uses OpenCV to read the frame, convert to RGB,
    and return the frame as a numpy array.

    Parameters
    ----------
    video_path : str
        The path to the video file.

    frame_number : int
        The frame number to read.

    Returns
    -------
    np.array
        The frame as a numpy array. The shape is (h, w, 3) and the dtype is uint8.
    """
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if not ret:
        raise ValueError(f"Could not read frame {frame_number} from {video_path}")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    cap.release()

    return frame


def timestamp_to_frame_num(timestamp: int, fps: float, force_floor: bool = True) -> int:
    """
    Given a timestamp and the FPS of the video, return the frame number.

    Parameters
    ----------
    timestamp : int
        The timestamp of the frame in seconds.
    fps : float
        The FPS of the video. This can be obtained by calling `get_fps`.
    force_floor : bool
        Whether to round the frame number down (floor) or not. This is set
        to True by default because one might get a float frame number due to
        the timestamp conversion, and rounding it down makes more sense than
        rounding it to closest, because the previously frame is still displayed
        at the time of the timestamp (i.e. the frame is not yet changed).
    """
    if not force_floor:
        return int(round(timestamp * fps))
    else:
        return int(timestamp * fps)


def frame_num_to_timestamp(frame_num: int, fps: float) -> float:
    """
    Given a frame number and the FPS of the video, return the timestamp.

    Parameters
    ----------
    frame_num : int
        The frame number.
    fps : float
        The FPS of the video. This can be obtained by calling `get_fps`.

    Returns
    -------
    float
        The timestamp of the frame in seconds.
    """
    return float(frame_num / fps)


def draw_bbox(im, intent, bbox, inplace=False, convert_to_rgb=True):
    """
    Draw the bounding box of the element targeted by the action on an image.

    Parameters
    ----------
    im : PIL.Image
        The image to draw on. This image will be modified in place unless `copy` is True.

    intent : str
        The type of event. It must be one of "click", "hover", "textInput", or "change".
        You can obtain it by calling `turn.intent`.

    bbox : dict
        The bounding box of the element targeted by the action. You can obtain it by calling
        `turn.element.get("bbox")`.

    inplace : bool
        Whether to modify the image in place or return a copy.

    convert_to_rgb : bool
        Whether to convert the image to RGB at the end. This is useful for saving to JPEG.

    Returns
    -------
    PIL.Image
        The image with the overlay drawn on it.
    """
    try:
        from PIL import ImageDraw
    except ImportError:
        raise ImportError(
            "You need to install the Pillow library (pip install Pillow) to use this function."
        )

    colors = {
        "click": "red",
        "hover": "orange",
        "textInput": "blue",
        "change": "green",
    }

    if not inplace:
        im = im.copy()

    im = im.convert("RGBA")

    draw = ImageDraw.Draw(im)

    # draw a bounding box around the element
    color = colors.get(intent, "purple")

    left = bbox["left"]
    top = bbox["top"]
    w = bbox["width"]
    h = bbox["height"]

    draw.rectangle((left, top, left + w, top + h), outline=color, width=2)

    if convert_to_rgb:
        im = im.convert("RGB")

    return im


def draw_at_xy(im, intent, x, y, inplace=False, convert_to_rgb=True):
    """
    Draw a red dot at some action's x and y coordinates on the image. This is only
    relevant when the intent is "click" or "hover".

    Parameters
    ----------
    im : PIL.Image
        The image to draw on. This image will be modified in place unless `copy` is True.

    intent : str
        The type of event. It must be one of "click", "hover", "textInput", or "change".
        You can obtain it by calling `turn.intent`.

    x : int
        The x coordinate of the action. You can obtain it by calling `turn.props.get("x")`.

    y : int
        The y coordinate of the action. You can obtain it by calling `turn.props.get("y")`.

    inplace : bool
        Whether to modify the image in place or return a copy.

    convert_to_rgb : bool
        Whether to convert the image to RGB at the end. This is useful for saving to JPEG.

    Returns
    -------
    PIL.Image
        The image with the overlay drawn on it.
    """
    try:
        from PIL import ImageDraw
    except ImportError:
        raise ImportError(
            "You need to install the Pillow library (pip install Pillow) to use this function."
        )

    colors = {
        "click": "red",
        "hover": "orange",
        "textInput": "blue",
        "change": "green",
    }

    if intent not in colors:
        raise ValueError(
            f"Invalid intent '{intent}'. It must be one of {list(colors.keys())}"
        )

    if not inplace:
        im = im.copy()

    im = im.convert("RGBA")

    draw = ImageDraw.Draw(im)

    color = colors[intent]

    if intent in ["click", "hover"]:
        r = 15
        for i in range(1, 5):
            rx = r * i
            draw.ellipse((x - rx, y - rx, x + rx, y + rx), outline=color, width=3)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    if convert_to_rgb:
        im = im.convert("RGB")

    return im
