from copy import deepcopy
import json
import logging
import math
from typing import TYPE_CHECKING

from ..utils.recs import is_list_monotonically_increasing, get_list_from_records_by_key
from .dom import get_tree_repr_simple

if TYPE_CHECKING:
    import lxml.html
    from transformers import PreTrainedTokenizer


def get_bracket_length(
    elem_open_bracket, elem_close_bracket, tokenizer: "PreTrainedTokenizer"
):
    """
    This function calculates the length of the brackets.

    Parameters
    ----------
    elem_open_bracket : str
        The opening bracket. For example, "<" or "[".

    elem_close_bracket : str
        The closing bracket. For example, ">" or "]".

    tokenizer : transformers.PreTrainedTokenizer
        The tokenizer to use to tokenize the brackets. This is used to calculate the length
        of the brackets.

    Returns
    -------
    int
        The length of the brackets.
    """
    if elem_open_bracket is None:
        elem_open_bracket = ""
    if elem_close_bracket is None:
        elem_close_bracket = ""

    elem_brackets = elem_open_bracket + elem_close_bracket
    bracket_length = len(tokenizer.tokenize(elem_brackets, add_special_tokens=False))

    return bracket_length


def reduce_list_of_lengths(lengths: list, max_length: int, assert_exactly_max=True):
    """
    Given a list of lengths, reduce the lengths to a maximum length. To learn more
    about how this is achieved, please read the strategic truncation section in the
    paper.

    Parameters
    ----------
    lengths : list
        A list of lengths to reduce.

    max_length : int
        The maximum length to reduce the list of lengths to.

    assert_exactly_max : bool, optional
        If True, then we will assert that the total length of the reduced list of lengths
        is exactly equal to max_length. Defaults to True. If False, then we will not
        assert this condition.

    Returns
    -------
    list
        The reduced list of lengths.

    Raises
    ------
    ValueError
        If the difference between the new total length and the max_length is negative.

    AssertionError
        If assert_exactly_max is True and the total length of the reduced list of lengths
        is not exactly equal to max_length. Also, if the lengths are not monotonically
        increasing (i.e., the lengths are not sorted by length).
    """
    # Assert lengths is monotonically increasing
    assert is_list_monotonically_increasing(lengths), "Lengths must be sorted by length"

    total_length = sum(lengths)

    if total_length <= max_length:
        return lengths

    if max_length <= 0:
        return [0] * len(lengths)

    # We will iterate through the records and calculate the cumulative sum of the lengths.
    # If at iteration i, the cumulative sum is greater than the max_length, then we will stop, then:
    # 1. Set the length of the subsequent records to be equal to the length of record i
    # 2. Calculate the difference between the cumulative sum and the max_length, call it `d`
    # 3. Reduce the length of the last `d` records by 1
    cumsum = 0
    new_lengths = []

    for i, length in enumerate(lengths):
        num_remaining_records = len(lengths) - i
        prev_length = lengths[i - 1] if i > 0 else 0
        increment_length_diff = length - prev_length

        # Note we are calculating the cumulative sum of the lengths of the remaining records
        # in terms of the incremental length difference
        cumsum += increment_length_diff * num_remaining_records

        if cumsum > max_length:
            # We have exceeded the max_length, so we need to truncate the records
            # We will truncate the records by setting the length of the subsequent records
            # to be equal to the length of record i
            break

        new_lengths.append(length)

    # Now, we need to reduce the length of the remaining records by the difference
    # between the cumulative sum and the max_length
    diff_per_rec = math.ceil((cumsum - max_length) / num_remaining_records)
    # We take the `length` of the record at index `i` and subtract the difference
    # to account for the increase
    final_length = length - diff_per_rec

    for j in range(i, len(lengths)):
        new_lengths.append(final_length)

    # Since diff_per_rec is rounded up, we may have removed more tokens than necessary
    # We will add the tokens back to the last N records, where N is the difference
    # between the new total length and the max_length
    diff = max_length - sum(new_lengths)

    if diff < 0:
        raise ValueError("Difference must be greater than or equal to 0.")

    for j in range(len(new_lengths) - diff, len(new_lengths)):
        new_lengths[j] += 1

    if assert_exactly_max:
        assert sum(new_lengths) == max_length, "Total length must be exactly max_length"

    return new_lengths


def get_truncation_offsets(tokens, length, num_tokens_to_remove):
    """
    This calculates the start and end offsets of the tokens to remove. This is a
    helper function for `truncate_text_at_center`.

    Parameters
    ----------
    tokens : dict
        The tokens to truncate. This should be a dictionary with the keys "input_ids"
        and "offset_mapping".

    length : int
        The length of the tokens.

    num_tokens_to_remove : int
        The number of tokens to remove from the tokens.

    Returns
    -------
    tuple
        A tuple of the start and end offsets of the tokens to remove.
    """
    # First, we need to find the center of the text, then take the tokens around it
    center = length // 2
    left = center - (num_tokens_to_remove // 2)
    right = left + num_tokens_to_remove

    # Now, we need to find the start and end offsets of the tokens
    start_offset = tokens["offset_mapping"][left][0]
    end_offset = tokens["offset_mapping"][right - 1][1]

    return start_offset, end_offset


def truncate_text_at_center(
    text: str,
    tokenizer: "PreTrainedTokenizer",
    tokens=None,
    max_tokens: int = 10,
    ellipsis: str = "...",
    ellipsis_length: int = None,
    assert_max_tokens=False,
    allow_retry_without_ellipsis=True,
    allow_iterative_reduction=False,
):
    """
    Parameters
    ----------
    allow_iterative_reduction: bool
        If True, then we will allow the iterative reduction to continue until the max_tokens is reached.
        This is useful when the tokenizer output does not necessarily decrease when we remove
        tokens from the input. For example, if we remove a token that is part of a word, but
        the updated text is retokenized to the same number of tokens, then we will continue
        to remove tokens until we reach the max_tokens limit.
    """
    # Only use the ellipsis if it is not None, if both ellipsis and ellipsis_length are None or
    # both are specified, then we raise an error
    if ellipsis is None and ellipsis_length is None:
        raise ValueError("Either ellipsis or ellipsis_length must be specified")

    if ellipsis_length is None:
        ellipsis_token = tokenizer.tokenize(ellipsis, add_special_tokens=False)
        ellipsis_length = len(ellipsis_token)

    if tokens is None:
        tokens = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)

    if hasattr(tokens, "ids") and hasattr(tokens, "offsets"):
        tokens = {
            "input_ids": tokens.ids,
            "offset_mapping": tokens.offsets,
        }

    init_text = text
    length = len(tokens["input_ids"])

    if length <= max_tokens:
        return {"text": text, "length": length}

    if max_tokens < ellipsis_length:
        # If we don't have enough tokens to allocate, then we should just remove the text
        return {"text": None, "length": 0}
    if max_tokens == ellipsis_length:
        return {"text": ellipsis, "length": ellipsis_length}

    num_tokens_to_remove = length - (max_tokens - ellipsis_length)
    start_offset, end_offset = get_truncation_offsets(
        tokens, length, num_tokens_to_remove
    )
    text = init_text[:start_offset] + ellipsis + init_text[end_offset:]

    if allow_iterative_reduction:
        is_smaller_or_equal = False

        while not is_smaller_or_equal:
            num_tokens_to_remove += 1
            start_offset, end_offset = get_truncation_offsets(
                tokens, length, num_tokens_to_remove
            )
            text = init_text[:start_offset] + ellipsis + init_text[end_offset:]
            new_tokens = tokenizer(text, add_special_tokens=False)
            is_smaller_or_equal = len(new_tokens["input_ids"]) <= max_tokens

    results = {"text": text}
    if assert_max_tokens or allow_retry_without_ellipsis:
        # Use tokenizer to calculate the number of tokens and assert it is equal to max_tokens
        tokens = tokenizer(text, add_special_tokens=False)
        is_smaller_or_equal = len(tokens["input_ids"]) <= max_tokens

        results["tokens"] = tokens

        if allow_retry_without_ellipsis and not is_smaller_or_equal:
            text = init_text[:start_offset] + init_text[end_offset:]
            tokens = tokenizer(text, add_special_tokens=False)
            is_smaller_or_equal = len(tokens["input_ids"]) <= max_tokens

        if assert_max_tokens:
            error_msg = f"# tokens must be less or equal to max_tokens={max_tokens}, got {len(tokens['input_ids'])}"
            assert is_smaller_or_equal, error_msg

    return results


def build_records_of_tokens_for_dom_tree(
    dom_tree: "lxml.html.HtmlElement",
    tokenizer: "PreTrainedTokenizer",
    sorted_by_length: bool = True,
):
    records = []
    for node in dom_tree.iter():
        if node.text is not None:
            text = node.text.strip()
        else:
            text = ""

        # text_tokens = tokenizer.tokenize(text, add_special_tokens=False)
        records.append(
            {
                "node": node,
                "type": "text",
                "text": text,
            }
        )

        for k, v in node.attrib.items():
            # value_tokens = tokenizer.tokenize(v, add_special_tokens=False)
            records.append(
                {
                    "node": node,
                    "key": k,
                    "type": "attrib",
                    "text": v,
                }
            )

    tokens = tokenizer(
        get_list_from_records_by_key(records, "text"),
        add_special_tokens=False,
        return_attention_mask=False,
        return_length=True,
    )
    lengths = tokens["length"]

    for i, r in enumerate(records):
        r["length"] = lengths[i]

    if sorted_by_length:
        records = sorted(records, key=lambda r: r["length"], reverse=False)

    return records


def truncate_dom_tree(
    dom_tree: "lxml.html.HtmlElement",
    tokenizer: "PreTrainedTokenizer",
    num_tokens_to_remove: int,
    ellipsis: str = "...",
    remove_when_none=True,
    copy=True,
    allow_iterative_reduction=False,
):
    """
    This function takes a dom tree and truncate it based on the number of tokens to remove.
    It is not guaranteed that the resulting dom tree will have the exact number of tokens
    as specified, but it will be close to the specified number of tokens. Please see
    `multi_attempt_truncate_dom_tree` for a more robust approach.

    Parameters
    ----------
    dom_tree : lxml.html.HtmlElement
        The dom tree to truncate.

    tokenizer : transformers.PreTrainedTokenizer
        The tokenizer to use to tokenize the text.

    num_tokens_to_remove : int
        The number of tokens to remove from the dom tree.

    ellipsis : str, optional
        The ellipsis to use to indicate that the text has been truncated. Defaults to "...".

    remove_when_none : bool, optional
        If True, then we will remove the attribute if the value is None. Defaults to True.

    copy : bool, optional
        If True, then we will copy the dom_tree before modifying it. Defaults to True.

    allow_iterative_reduction: bool
        If True, then we will allow the iterative reduction to continue until the max_tokens is reached.
        This is useful when the tokenizer output does not necessarily decrease when we remove
        tokens from the input. For example, if we remove a token that is part of a word, but
        the updated text is retokenized to the same number of tokens, then we will continue
        to remove tokens until we reach the max_tokens limit.

    Returns
    -------
    lxml.html.HtmlElement
        The truncated dom tree.
    """
    # Unlike the naive approach, we will remove the tokens starting from the node
    # with the most tokens, then work our way down until we have removed the
    # specified number of tokens.
    if copy:
        dom_tree = deepcopy(dom_tree)

    ellipsis_length = len(tokenizer.tokenize(ellipsis, add_special_tokens=False))
    # Note: We only count the token lengths of the values, not the entire formatted string
    # The full string may have additional tokens (key, separator, etc.)
    # Consequently, max_total_length is different from max_tokens
    records = build_records_of_tokens_for_dom_tree(
        dom_tree, tokenizer, sorted_by_length=True
    )

    lengths_orig = get_list_from_records_by_key(records, "length")
    max_total_length = sum(lengths_orig) - num_tokens_to_remove
    lengths_reduced = reduce_list_of_lengths(lengths_orig, max_length=max_total_length)

    for i, r in enumerate(records):
        red_length = lengths_reduced[i]
        # If the length is the same, then we don't need to do anything
        if red_length >= r["length"]:
            continue

        # If the reduced length is 0 (but original is not), then we should remove the node
        if red_length == 0:
            if r["type"] == "text":
                r["node"].text = None

            elif r["type"] != "attrib":
                raise ValueError(
                    f"Unknown type: {r['type']}. Must be 'text' or 'attrib'"
                )

            elif remove_when_none and r["text"] is None:
                r["node"].attrib.pop(r["key"])

            else:
                r["node"].attrib[r["key"]] = None

            continue

        # Otherwise, we need to truncate the text
        trunc = truncate_text_at_center(
            r["text"],
            tokenizer=tokenizer,
            max_tokens=red_length,
            ellipsis_length=ellipsis_length,
            allow_iterative_reduction=allow_iterative_reduction,
        )

        if r["type"] == "text":
            r["node"].text = trunc["text"]

        elif r["type"] != "attrib":
            raise ValueError(f"Unknown type: {r['type']}. Must be 'text' or 'attrib'")

        elif remove_when_none and trunc["text"] is None:
            r["node"].attrib.pop(r["key"])

        else:
            r["node"].attrib[r["key"]] = trunc["text"]

    return dom_tree


def multi_attempt_truncate_dom_tree(
    dom_tree: "lxml.html.HtmlElement",
    tokenizer: "PreTrainedTokenizer",
    ellipsis: str = "...",
    max_attempts=5,
    max_tokens=700,
    warn_after_attempts=True,
    copy_tree=True,
    compute_final_num_tokens=False,
    allow_iterative_reduction=False,
):
    """ "
    This will attempt to truncate the dom_tree to the specified number of tokens.
    THe reason we need more than one attempt is because when we specify a number
    of tokens to remove based on a max_tokens value, the resulting number of tokens
    may be greater than the max_tokens value, due to how tokenizers work. Therefore,
    we need to try multiple times to truncate the dom_tree to the specified number.
    If after max_attempts, we are still unable to truncate the dom_tree to the
    specified number of tokens, then we will truncate the resulting text directly.
    """
    for num_attempts in range(max_attempts):
        tree_repr = get_tree_repr_simple(dom_tree)
        tokens = tokenizer.tokenize(tree_repr, add_special_tokens=False)
        num_tokens = len(tokens)

        if num_tokens <= max_tokens:
            results = {"dom_tree": dom_tree, "tree_repr": tree_repr}
            if compute_final_num_tokens:
                results["num_tokens"] = num_tokens

            return results

        dom_tree = truncate_dom_tree(
            dom_tree=dom_tree,
            tokenizer=tokenizer,
            num_tokens_to_remove=num_tokens - max_tokens,
            ellipsis=ellipsis,
            remove_when_none=num_attempts > 1,
            copy=copy_tree,
            allow_iterative_reduction=allow_iterative_reduction,
        )
    if warn_after_attempts:
        logging.warning(
            "Reached max # of attempts when trying to run `truncate_dom_tree`. "
            "We will be truncating the text directly."
        )

    tree_repr = get_tree_repr_simple(dom_tree)
    trunc = truncate_text_at_center(
        tree_repr,
        tokenizer=tokenizer,
        max_tokens=max_tokens,
        allow_iterative_reduction=allow_iterative_reduction,
    )
    tree_repr = trunc["text"]
    results = {"dom_tree": dom_tree, "tree_repr": tree_repr}

    if compute_final_num_tokens:
        num_tokens = len(tokenizer.tokenize(tree_repr, add_special_tokens=False))
        results["num_tokens"] = num_tokens

    return results


def convert_elem_dict_to_str(elem_dict: dict, remove_empty=False):
    """
    Convert an element dictionary to a string.

    Parameters
    ----------
    elem_dict : dict
        The element dictionary.

    remove_empty : bool, optional
        If True, then we will remove any empty elements. Defaults to False.

    Returns
    -------
    str
        The string representation of the element dictionary.
    """
    elem_dict = deepcopy(elem_dict)
    element_str = ""

    for elem in ["tag", "xpath", "text", "bbox", "attributes", "children"]:
        if elem not in elem_dict:
            continue
        value = elem_dict.pop(elem)
        if remove_empty and value in [None, ""]:
            continue

        element_str += f"[[{elem}]] {value}\n"

    # for other keys, we just add them to the end

    for k, v in elem_dict.items():
        if remove_empty and v in [None, ""]:
            continue
        element_str += f"\n[[{k}]] {v}"

    return element_str


def truncate_cands_turn(
    cands_turn: list,
    tokenizer: "PreTrainedTokenizer",
    num_tokens_to_remove: int,
    protected_elem_keys=("tag", "bbox"),
    copy: bool = True,
    remove_empty=True,
    allow_iterative_reduction=False,
):
    """
    This truncates the candidates turn to the specified number of tokens. This is useful
    when the candidates turn is too long, and we need to truncate it to fit within the
    maximum token length.

    Parameters
    ----------
    cands_turn : list
        The candidates turn to truncate.

    tokenizer : transformers.PreTrainedTokenizer
        Th tokenizer to use to tokenize the text.

    num_tokens_to_remove : int
        The number of tokens to remove from the candidates turn.

    protected_elem_keys : tuple, optional
        The keys to protect from truncation. Defaults to ("tag", "bbox").

    copy : bool, optional
        If True, then we will copy the candidates turn before modifying it. Defaults to True.

    remove_empty : bool, optional
        If True, then we will remove any empty elements. Defaults to True.

    allow_iterative_reduction: bool
        If True, then we will allow the iterative reduction to continue until the max_tokens is reached.
        This is useful when the tokenizer output does not necessarily decrease when we remove
        tokens from the input. For example, if we remove a token that is part of a word, but
        the updated text is retokenized to the same number of tokens, then we will continue
        to remove tokens until we reach the max_tokens limit.

    Returns
    -------
    list
        The truncated candidates turn.
    """
    if num_tokens_to_remove <= 0:
        return cands_turn

    protected_elem_keys = set(protected_elem_keys)
    if copy:
        cands_turn = deepcopy(cands_turn)
    records = []

    # Otherwise, we need to truncate the candidates turn
    for t, cand in enumerate(cands_turn):
        for key, value in cand["elem_dict"].items():
            if key in protected_elem_keys:
                continue

            if value is None:
                continue

            if isinstance(value, (int, float)):
                value_str = str(value)

            elif isinstance(value, (list, dict)):
                value_str = json.dumps(value)

            else:
                value_str = value

            tokens = tokenizer.tokenize(value_str, add_special_tokens=False)

            records.append(
                {
                    "index": t,
                    "key": key,
                    "value": value_str,
                    "cand": cand,
                    "tokens": tokens,
                    "length": len(tokens),
                }
            )
    # Note: We only count the token lengths of the values, not the entire formatted string
    # The full string may have additional tokens (key, separator, etc.)
    # Consequently, max_total_length is different from max_tokens
    records = sorted(records, key=lambda r: r["length"])
    lengths_orig = get_list_from_records_by_key(records, "length")
    max_total_length = sum(lengths_orig) - num_tokens_to_remove
    lengths_reduced = reduce_list_of_lengths(lengths_orig, max_length=max_total_length)

    for i, rec in enumerate(records):
        red_length = lengths_reduced[i]
        # If the length is the same, then we don't need to do anything
        if red_length >= rec["length"]:
            continue
        # Otherwise, we need to truncate the text
        trunc = truncate_text_at_center(
            rec["value"],
            tokenizer=tokenizer,
            max_tokens=red_length,
            allow_iterative_reduction=allow_iterative_reduction,
        )

        cands_turn[rec["index"]]["elem_dict"][rec["key"]] = trunc["text"]

    # Finally, we update cands_turn[i]["doc"] to reflect the changes
    for cand in cands_turn:
        cand["doc"] = convert_elem_dict_to_str(
            cand["elem_dict"], remove_empty=remove_empty
        )

    return cands_turn


def multi_attempt_truncate_cands_turn(
    cands_turn: list,
    tokenizer: "PreTrainedTokenizer",
    max_tokens: int,
    format_candidates_fn,
    max_attempts: int = 5,
    warn_after_attempts: bool = True,
    protected_elem_keys=("tag", "bbox"),
    allow_iterative_reduction=False,
):
    """
    This is a more robust version of `truncate_cands_turn`. It will attempt to truncate
    the candidates turn to the specified number of tokens. If after max_attempts, we are
    still unable to truncate the candidates turn to the specified number of tokens, then
    we will truncate the resulting text directly, as a last resort.
    """
    for _ in range(max_attempts + 1):
        cands_turn_str = format_candidates_fn(cands_turn, max_char_len=None)
        cands_turn_tokens = tokenizer.tokenize(cands_turn_str, add_special_tokens=False)

        num_tokens_to_remove = len(cands_turn_tokens) - max_tokens

        if num_tokens_to_remove <= 0:
            return cands_turn

        cands_turn = truncate_cands_turn(
            cands_turn=cands_turn,
            tokenizer=tokenizer,
            num_tokens_to_remove=num_tokens_to_remove,
            protected_elem_keys=protected_elem_keys,
            allow_iterative_reduction=allow_iterative_reduction,
        )

    if warn_after_attempts:
        logging.warning(f"Reached max # of attempts to truncate cands_turn ")

    # We will try to truncate the text directly
    tokens_no_format = tokenizer.tokenize(
        " ".join([cand["doc"] for cand in cands_turn]),
        add_special_tokens=False,
    )
    sep_len = math.ceil(
        (len(cands_turn_tokens) - len(tokens_no_format)) / len(cands_turn)
    )
    num_tokens_remaining = max_tokens
    num_cands_remaining = len(cands_turn)

    for cand in cands_turn:
        trunc = truncate_text_at_center(
            cand["doc"],
            tokenizer=tokenizer,
            max_tokens=math.ceil(num_tokens_remaining / num_cands_remaining),
            allow_iterative_reduction=allow_iterative_reduction,
        )
        cand["doc"] = trunc["text"]
        tokens = tokenizer.tokenize(trunc["text"], add_special_tokens=False)
        num_tokens_remaining -= len(tokens) + sep_len
        num_cands_remaining -= 1

    return cands_turn
