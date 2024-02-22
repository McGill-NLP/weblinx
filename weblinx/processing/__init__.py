from pathlib import Path
from tqdm import tqdm

from ..utils.recs import group_record_to_dict

from . import dom, prompt, outputs, truncation


def load_candidate_elements(path, group_keys=("demo_name", "turn_index"), log_fn=None):
    """
    This will load the candidates from the path.

    `group_keys` is used to group the candidates by the specified keys, which will be returned
    as a dictionary of lists, where the keys are the values of the specified keys, and the values
    are the list of candidates that have the same value for the specified keys. If `group_keys` is
    None, then the candidates will not be grouped, and will be returned as a list.

    For example, if `group_keys` is ("demo_name", "turn_index"), then the candidates will be
    ```
    {
        ("demo1", 0): [c1, c2, c3, ...],
        ("demo1", 1): [c4, c5, c6, ...],
        ("demo2", 0): [c7, c8, c9, ...],
        ...
    }
    ```

    Whereas if `group_keys` is None, then the candidates will be
    ```
    [c1, c2, c3, c4, c5, c6, c7, c8, c9, ...]
    ```

    Candidates are elements that could potentially be used as the target output for the model.
    For example, if the goal is to click on a button, you may find a button element as a candidate,
    if the original candidate ranking model does a good job at ranking the candidates.

    Parameters
    ----------
    path : str
        The path to the candidates file. This can be a JSONL file.
    group_keys : tuple[str], optional
        The keys to use to group the candidates. If None, then the candidates will not be grouped.

    Returns
    -------
    list or dict
        The candidates, either as a list or as a dictionary of lists.

    Example
    --------
    Here's an example of how to use this function:
    ```
    candidates = load_candidate_elements("candidates.jsonl", group_keys=("demo_name", "turn_index"))
    ```

    This will load the candidates from the file "candidates.jsonl" and group them by the keys "demo_name"
    and "turn_index". The candidates will be returned as a dictionary of lists.
    """
    try:
        import ujson as json
    except:
        import json

    candidates_path = Path(path).expanduser()
    candidates = []
    with open(candidates_path) as f:  # jsonl
        for line in tqdm(f, desc="Loading candidates"):
            candidates.append(json.loads(line))
    if group_keys is not None:
        candidates = group_record_to_dict(candidates, keys=group_keys, copy=False)

    if log_fn is not None:
        log_fn(f"Loaded {len(candidates)} candidates from {candidates_path}.")

    return candidates
