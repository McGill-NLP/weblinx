"""
A module dedicated to manipulating and working with lists and records (which are list of dictionaries).
"""

from copy import deepcopy
from collections import defaultdict
from typing import Any, List, Dict


def is_list_monotonically_increasing(lst: list) -> bool:
    """
    This function checks if a list is monotonically increasing.

    Parameters
    ----------
    lst : list
        The list to check.

    Returns
    -------
    bool
        True if the list is monotonically increasing, False otherwise.
    """
    l = lst[0]
    for x in lst[1:]:
        if x < l:
            return False
        l = x

    return True


def get_list_from_records_by_key(records: dict, key: str) -> list:
    """
    For a given key, return a list of values from the records
    taken from the key.

    Parameters
    ----------
    records : dict
        A list of dictionaries to extract the values from.

    key : str
        The key to extract from the records.

    Returns
    -------
    list
        A list of values from the records based on the key.
    """
    return [r[key] for r in records]


def insert_list_into_records_by_key(records: dict, key: str, lst: list) -> None:
    """
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

    Parameters
    ----------
    records : dict
        A list of dictionaries to insert the list into.

    key : str
        The key to insert the list into.

    lst : list
        The list to insert into the records.
    """
    assert len(records) == len(lst), "Records and list must be the same length"
    for i in range(len(records)):
        records[i][key] = lst[i]


def group_record_to_dict(
    records: List[dict], keys, remove_keys=False, copy=True
) -> Dict[Any, List[dict]]:
    """
    Given a list of dictionaries, this function groups the dictionaries by the
    keys specified in `keys`. The keys in `keys` must be present in all
    dictionaries. The end result is a dictionary of dictionaries, where the
    key is a tuple of (val1, val2, ...) corresponding to key1, key2, etc.,
    and the value is a subset of the original list of dictionaries.

    Parameters
    ----------
    records: List[dict]
        A list of dictionaries to be grouped.
    keys: List[str]
        The keys to group by. They must be present in all dictionaries.
    remove_keys: bool
        Whether to remove the keys from the dictionaries in the output.
    copy: bool
        Whether to copy the dictionaries in the output before returning. If
        False, then the dictionaries of the input records will be modified in place.
    """
    grouped = defaultdict(list)
    for record in records:
        if copy:
            record = deepcopy(record)

        key = tuple(record[k] for k in keys)
        if remove_keys:
            for k in keys:
                del record[k]

        grouped[key].append(record)

    return dict(grouped)


def ungroup_dict_to_records(grouped_records: dict, restore_keys: list = None) -> list:
    """
    Given a dictionary of grouped records, this function restores the keys
    specified in `restored_keys` and returns a list of dictionaries. If the
    `restored_keys` is None, then the keys are not restored.

    Parameters
    ----------
    grouped_records : dict
        A dictionary of grouped records, which means the keys are tuples and the
        values are lists of dictionaries.

    restore_keys : list
        The keys to restore. If None, then the keys are not restored.

    Returns
    -------
    list
        A list of dictionaries.

    Example
    --------

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
    """
    if restore_keys is not None:
        k_len = len(restore_keys)
        # Verify that all the keys are tuples and the length of the tuples are the same
        for k in grouped_records.keys():
            if not isinstance(k, tuple):
                raise ValueError(f"Key {k} is not a tuple")
            if len(k) != k_len:
                raise ValueError(
                    f"Length of key {k} ({len(k)}) != length of `restored_keys` ({k_len})"
                )

    records = []

    for k, v in grouped_records.items():
        for r in v:
            # Add back the matched restored keys with the values in `k`
            record = {}
            if restore_keys is not None:
                for i, restored_key in enumerate(restore_keys):
                    record[restored_key] = k[i]

            # Add back the rest of the keys
            record.update(r)
            records.append(record)

    return records
