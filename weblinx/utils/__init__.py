"""
This contains a collection of utility functions, and include submodules for different categories of utility functions.
"""

from pathlib import Path
import hashlib
import json
from importlib.util import find_spec

from . import url, envs, html, recs


def shorten_text(s, max_length=100):
    # shorten to 100 characters
    if len(s) > max_length:
        s = s[:max_length] + "..."

    return s


def get_nums_from_path(path):
    """
    Finds the first and second number in a path. The path should follow the
    following pattern: <prefix>-<num_1>-<num_2>.<ext>, e.g. `screenshot-15-1.png`
    or `page-15-1.html`, which would return `15` and `1` for both cases.
    """
    path = Path(path)
    name = path.with_suffix("").name

    num_1, num_2 = map(int, name.split("-")[-2:])
    return num_1, num_2


def rank_paths(path, max_num_2=1, epsilon=1):
    """
    This function can be used to rank file names for sorting purposes. It assumes
    the file will follow the following pattern: <prefix>-<num_1>-<num_2>.<ext>, e.g.
    `screenshot-15-1.png`. Note that `max_num_2` is used to normalize the second
    number, so that the first number is more important. For example, if `max_num_2`
    is 10, then the second number will be divided by 10 before being multiplied by
    the first number. This means that `screenshot-15-1.png` will be ranked higher.

    epsilon is used to ensure that the second part does reach 1.0, which would
    make it equal to num_1 + 1, creating an undesired tie.
    """
    num_1, num_2 = get_nums_from_path(path)
    denom = (
        float(max_num_2) + epsilon
    )  # Denom is used to normalize the second number so it is under 1.

    return float(num_1) + (float(num_2) / denom)


def hash_file(path, method="md5", error_on_missing=True):
    """
    Given a path to a file, this function will return the hash in hex of the file.
    It can use either the md5 or sha256 method.

    If error_on_missing is True, then this function will raise a FileNotFoundError
    if the file does not exist. Otherwise, it will return None.
    """
    if method == "md5":
        hasher = hashlib.md5()

    elif method == "sha256":
        hasher = hashlib.sha256()

    else:
        raise ValueError("hash_file's 'method' arg must be either md5 or sha256")

    path = Path(path)
    if not path.exists():
        if error_on_missing:
            raise FileNotFoundError(f"File {path} does not exist")
        else:
            return None

    with open(path, "rb") as f:
        hasher.update(f.read())

    return hasher.hexdigest()


def hash_str(s, method="md5"):
    """
    Given a string, this function will return the hash in hex of the string.
    It can use either the md5 or sha256 method.
    """
    if method == "md5":
        hasher = hashlib.md5()

    elif method == "sha256":
        hasher = hashlib.sha256()

    else:
        raise ValueError("hash_str's 'method' arg must be either md5 or sha256")

    hasher.update(s.encode("utf-8"))

    return hasher.hexdigest()


def hash_json(data, method="md5"):
    """
    Given a json object, this function will return the hash in hex of the json.
    It can use either the md5 or sha256 method.
    """
    if method == "md5":
        hasher = hashlib.md5()

    elif method == "sha256":
        hasher = hashlib.sha256()

    else:
        raise ValueError("hash_json's 'method' arg must be either md5 or sha256")

    hasher.update(json.dumps(data, sort_keys=True).encode("utf-8"))

    return hasher.hexdigest()


def hex_to_int(hex_str):
    """
    Given a hex string, this function will return the integer value of the hex.
    If there is any non hex character, it will be ignored.
    """
    hex_clean = "".join([c for c in hex_str if c in "0123456789abcdef"])
    return int(hex_clean, 16)


def load_demo_names_in_split(
    split_path, split="train", sample_size=None, random_state=42
):
    """
    Loads a split from a json file. The json file should be a dictionary with
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
    demo_names : list of str
        The list of demo names corresponding to the split. If sample_size is
        not None, then this will be a random sample of the specified size.
    """
    split_path = Path(split_path).expanduser()

    with open(split_path) as f:
        splits = json.load(f)

    demo_names = splits[split]

    if sample_size is not None:
        import random

        random.seed(random_state)
        demo_names = random.sample(demo_names, sample_size)

    return demo_names


def auto_read_json(path, backend="auto"):
    path = str(path)
    if backend in ["auto", "orjson"] and find_spec("orjson"):
        import orjson

        backend = "orjson"

    elif backend in ["auto", "ujson"] and find_spec("ujson"):
        import ujson

        backend = "ujson"

    else:
        import json

        backend = "json"

    with open(path) as f:
        if backend == "json":
            data = json.load(f)
        elif backend == "ujson":
            data = ujson.load(f)
        elif backend == "orjson":
            data = orjson.loads(f.read())
        else:
            raise ValueError(
                f"Invalid backend '{backend}'. Must be either 'auto', 'json', 'ujson', or 'orjson'"
            )

    return data



def auto_save_json(data, path, backend="auto", indent=0):
    if indent is None:
        indent = 0
    
    path = str(path)
    if backend in ["auto", "orjson"] and find_spec("orjson") and indent not in [2, 0]:
        import orjson

        backend = "orjson"

    elif backend in ["auto", "ujson"] and find_spec("ujson"):
        import ujson

        backend = "ujson"

    else:
        import json

        backend = "json"

    if backend == "json":
        with open(path, "w") as f:
            json.dump(data, f, indent=indent)
    elif backend == "ujson":
        with open(path, "w") as f:
            ujson.dump(data, f, indent=indent)
    elif backend == "orjson":
        if indent == 2:
            option = orjson.OPT_INDENT_2
        elif indent == 0:
            option = None
        else:
            raise ValueError(
                f"Invalid indent value {indent}. Must be either 2, 4, or None"
            )
        with open(path, "wb") as f:
            f.write(orjson.dumps(data, option=option))
    else:
        raise ValueError(
            f"Invalid backend '{backend}'. Must be either 'auto', 'json', 'ujson', or 'orjson'"
        )


def save_results(results, result_dir, filename="results.json"):
    result_dir = Path(result_dir).expanduser()
    result_dir.mkdir(parents=True, exist_ok=True)
    with open(result_dir / filename, "w") as f:
        json.dump(results, f, indent=2)


def set_seed(seed):
    import random

    random.seed(seed)

    try:
        import numpy as np

        np.random.seed(seed)

    except ImportError:
        pass

    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    except ImportError:
        pass

    except Exception as e:
        print(f"Error setting seed for torch: {e}")


def filter_records(records: list, **kwargs):
    """
    Given an input `records` (a list of dictionaries), this finds all the records that
    match the given kwargs. For example, if records is a list of records
    that contain a "demo_name" key and a "turn_index" key, then you can
    find all records that match a given demo_name and turn_index by doing
    find_record(records, demo_name="demo_1", turn_index=0).
    """
    matches = []
    for record in records:
        is_match = True
        for k, v in kwargs.items():
            if record[k] != v:
                is_match = False
                break

        if is_match:
            matches.append(record)

    return matches
