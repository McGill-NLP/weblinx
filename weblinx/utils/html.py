from copy import deepcopy


def has_elem_in_viewport(
    turn,
    attrib_dict: dict,
    key="data-webtasks-id",
    min_height=2,
    min_width=2,
    verbose=False,
):
    """
    Given a turn and an element's attributes, check if the element is in the viewport.

    Parameters
    ----------
    turn : webtasks.Turn
        The turn to check.
    attrib_dict : dict
        The element's attributes, as a dictionary. If you use lxml.html, you can get this
        by calling `elem.attrib`. For bs4, you can get this by calling `elem.attrs`.
        For example: `{"data-webtasks-id": "1234", "class": "foo bar"}`
    key : str, optional
        The key to use to find the element's ID.
    min_height : int, optional
        The minimum height of the element to be considered in the viewport. Defaults to 2.
    min_width : int, optional
        The minimum width of the element to be considered in the viewport. Defaults to 2.
    verbose : bool, optional
        Whether to print out debug statements. Defaults to False.
    """
    if turn is None:
        return False

    if turn.bboxes is None:
        if verbose:
            print(f"[i={turn.index}] No bboxes")
        return False

    if key not in attrib_dict:
        if verbose:
            print(f"[i={turn.index}] No {key} attribute")
        return False

    if (wid := attrib_dict[key]) not in turn.bboxes:
        if verbose:
            print(f"[i={turn.index}] No bbox for {key}={wid}")
        return False

    box = turn.bboxes[wid]

    if box is None:
        if verbose:
            print(f"[i={turn.index}] No bbox for {key}={wid}")
        return False

    if box["width"] < min_width or box["height"] < min_height:
        return False

    if turn.viewport_width is None or turn.viewport_height is None:
        return True

    if box["x"] > turn.viewport_width or box["y"] > turn.viewport_height:
        return False

    return True


def open_html_with_encodings(path, encodings=["utf-8", "latin-1"], raise_error=True):
    """
    Open an HTML file with a list of encodings.

    Parameters
    ----------
    path : str
        The path to the HTML file.
    encodings : list, optional
        A list of encodings to try. Defaults to ["utf-8", "latin-1"].
    raise_error : bool, optional
        Whether to raise an error if the file cannot be opened. Defaults to True.
        If False, returns None if the file cannot be opened.

    Returns
    -------
    lxml.html.HtmlElement
        The HTML element.
    """
    for encoding in encodings:
        try:
            with open(path, encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            if raise_error:
                raise
            else:
                return None
    if raise_error:
        raise ValueError(f"Could not open {path} with encodings {encodings}")
    else:
        return None


def filter_bboxes(
    bboxes, min_height=10, min_width=10, viewport_height=None, viewport_width=None
):
    """
    Given the bboxes of a turn, filter out bboxes if:
    - The bbox is smaller than the minimum height and minimum width (one of them must be satisfied)
    - The bbox is outside the viewport (if viewport_height or viewport_width is not None)

    Parameters
    ----------
    bboxes : dict
        The bboxes of the turn.

    min_height : int, optional
        The minimum height of the bbox. Defaults to 10.

    min_width : int, optional
        The minimum width of the bbox. Defaults to 10.

    viewport_height : int, optional
        The height of the viewport. If not None, then bboxes with y > viewport_height are filtered out.
        Defaults to None.

    viewport_width : int, optional
        The width of the viewport. If not None, then bboxes with x > viewport_width are filtered out.
        Defaults to None.

    Returns
    -------
    dict
        The filtered bboxes that satisfy the conditions.s
    """
    remaining_bboxes = {}

    for wid, box in bboxes.items():
        # The width and height must be positive
        if box["width"] <= 0 or box["height"] <= 0:
            continue

        if box["width"] < min_width and box["height"] < min_height:
            continue
        if viewport_height is not None and box["y"] > viewport_height:
            continue
        if viewport_width is not None and box["x"] > viewport_width:
            continue
        remaining_bboxes[wid] = box

    return remaining_bboxes
