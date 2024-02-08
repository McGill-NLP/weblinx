from functools import partial
from multiprocessing.pool import Pool, ThreadPool
import json
import logging
import math
from typing import TYPE_CHECKING, Callable, List

from tqdm.auto import tqdm

from .. import filter_turns, Turn, Replay
from ..utils.recs import get_list_from_records_by_key
from ..utils.format import format_output_dictionary, format_timestamp
from .truncation import reduce_list_of_lengths, truncate_text_at_center


if TYPE_CHECKING:
    # imports for type hints and annotations
    from transformers import PreTrainedTokenizer


def get_speaker(
    utterance, instructor_name="User", navigator_name="Assistant", default_name=None
):
    """
    This will return the speaker for the utterance. If the utterance does not start with "say",
    then it will return the navigator's name. If the utterance starts with "say", then it will
    return the instructor's name if the speaker is "instructor", and the navigator's name if the
    speaker is "navigator". If the speaker is neither "instructor" nor "navigator", then it will
    return the default name, if it is not None. If the default name is None, then it will raise
    a ValueError.

    Parameters
    ----------
    utterance : str
        The utterance to get the speaker for.

    instructor_name : str, optional
        The name of the instructor. Defaults to "User".

    navigator_name : str, optional
        The name of the navigator. Defaults to "Assistant".

    default_name : str, optional
        The default name to use if the speaker is neither "instructor" nor "navigator". If None,
        then it will raise a ValueError. Defaults to None.

    Returns
    -------
    str
        The speaker for the utterance.
    """
    if not utterance.startswith("say"):
        return navigator_name
    elif 'speaker="instructor"' in utterance:
        return instructor_name
    elif 'speaker="navigator"' in utterance:
        return navigator_name
    elif default_name is not None:
        return default_name
    else:
        raise ValueError(
            f"Unknown speaker for utterance: {utterance}. To avoid this error, set default_name."
        )


def identity(x):
    """
    Simply returns the input. Needed for the `format_intent` parameter in `format_prev_turns_truncated`.

    Parameters
    ----------
    x : any
        The input to return.

    Returns
    -------
    any
        The input.
    """
    return x


def format_prev_turns(replay, turn, format_intent, turn_sep=" ; ", num_prev_turns=5):
    """
    Formats the previous turns (up until but not including `turn`) as a string, or as
    a list if turn_sep is `None`. The previous turns are formatted using the `format_intent`
    which is a function that takes a turn and returns a string or a dictionary. This function
    is useful for displaying the previous turns as context for the current turn. This information
    is used by the action model to predict the next action.

    Parameters
    ----------
    replay : Replay
        The replay to get the previous turns from.

    turn : Turn
        The turn to get the previous turns for.

    format_intent : Callable
        A function that takes a turn and returns a string or a dictionary.

    turn_sep : str, optional
        The separator to use for joining the previous turns. If None, then the previous turns
        are returned as a list. Defaults to " ; ".

    num_prev_turns : int, optional
        The number of previous turns to include. Defaults to 5.

    Returns
    -------
    str or list
        The previous turns formatted as a string, or as a list if turn_sep is None.
    """
    start_index = max(0, turn.index - num_prev_turns)
    prev_turns = replay[start_index : turn.index]
    prev_turns_formatted = [format_intent(turn, return_as=str) for turn in prev_turns]

    if turn_sep is not None:
        return turn_sep.join(prev_turns_formatted)
    else:
        return prev_turns_formatted


def format_candidates(candidates, max_char_len=300, use_uid_as_rank=False):
    """
    This will format the candidates as a string. The candidates are formatted as follows:
    1. If there are no candidates, return ""
    2. If there are candidates, return the candidates as a string, with the rank (e.g. uid) and document (text representation of the candidate)
    3. If the document is longer than `max_char_len`, then it will be truncated to `max_char_len`

    Parameters
    ----------
    candidates : list
        The candidates to format.

    max_char_len : int, optional
        The maximum character length for the document. If the document is longer than this, then it will
        be truncated to this length. Defaults to 300.

    use_uid_as_rank : bool, optional
        Whether to use the UID as the rank. If False, then it will use the rank from the candidates.
        Defaults to False.

    Returns
    -------
    str
        The candidates formatted as a string.
    """
    s = ""
    for cand in candidates:
        doc = cand["doc"].replace("\n", " ")
        if use_uid_as_rank:
            rank = "uid = " + cand["uid"]
        else:
            rank = cand["rank"]

        if max_char_len is not None and len(doc) > max_char_len:
            doc = doc[: max_char_len - 3] + "..."

        s += f"({rank}) {doc}\n"
    return s


def format_utterances(
    turns,
    num_utterances=5,
    type_filter="chat",
    sep=" ",
    convert_to_minutes=True,
    template="[{timestamp}] {utterance}",
):
    """
    Formats utterances from a list of turns. The utterances are formatted as follows:
    1. If there are no utterances, return "No instructor utterance"
    2. If there are less than `num_utterances` utterances, return all utterances
    3. If there are more than `num_utterances` utterances, return the first and last `num_utterances-1` utterances

    If sep is None, then the utterances are returned as a list. Otherwise, they are joined by `sep`.

    Parameters
    ----------
    turns : list
        The list of turns to get the utterances from.

    num_utterances : int, optional
        The number of utterances to include. Defaults to 5.

    type_filter : str, optional
        The type of turn to include. If None, then it will include all types. Defaults to "chat".

    sep : str, optional
        The separator to use for joining the utterances. If None, then the utterances are returned as a list.
        Defaults to " ".

    convert_to_minutes : bool, optional
        Whether to convert the timestamp to minutes. Defaults to True.

    template : str, optional
        The template to use for formatting the utterances. Defaults to "[{timestamp}] {utterance}".

    Returns
    -------
    str or list
        The utterances formatted as a string, or as a list if sep is None.
    """
    if type_filter is not None:
        turns = [turn for turn in turns if turn.type == type_filter]

    if len(turns) <= 0:
        return "No instructor utterance"

    # We select the first utterance and last `num_utterances-1` utterances
    elif len(turns) <= num_utterances:
        selected_turns = turns
    else:
        # We take the first two and last two turns
        selected_turns = turns[0:1] + turns[-num_utterances:]

    texts = []
    for turn in selected_turns:
        turn_dict = {k: v for k, v in turn.items()}
        if convert_to_minutes:
            turn_dict["timestamp"] = format_timestamp(turn, return_as=str)
        texts.append(template.format(**turn_dict))

    if sep is None:
        utterance_context = texts
    else:
        utterance_context = sep.join(texts)

    return utterance_context


def format_prev_turns_truncated(
    replay: "Replay",
    turn: "Turn",
    format_intent,
    tokenizer: "PreTrainedTokenizer",
    num_tokens_to_remove: int,
    format_output_dict_fn: Callable = format_output_dictionary,
    num_prev_turns: int = 5,
    turn_sep: str = " ; ",
    allow_iterative_reduction=False,
):
    """
    This performs the same function as `format_prev_turns`, but it truncates the text
    to fit within the `max_tokens`. The truncation is not a regular truncation, instead
    it uses the `truncate_text_at_center` function (see strategic trunction part
    in the paper).
    """
    start_index = max(0, turn.index - num_prev_turns)
    prev_turns = replay[start_index : turn.index]
    prev_turns_lst = [format_intent(turn, return_as=dict) for turn in prev_turns]
    prev_turns_fmt_lst = [format_output_dict_fn(turn) for turn in prev_turns_lst]

    if turn_sep is not None:
        prev_turns_formatted = turn_sep.join(prev_turns_fmt_lst)
    else:
        prev_turns_formatted = " ; ".join(prev_turns_fmt_lst)

    if num_tokens_to_remove <= 0:
        if turn_sep is not None:
            return prev_turns_formatted
        else:
            return prev_turns_fmt_lst

    records = []

    for t, turn_formatted in enumerate(prev_turns_lst):
        for key, value in turn_formatted.items():
            if key == "intent":
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
                    "text": value_str,
                    "turn_formatted": turn_formatted,
                    "original_value_type": type(value),
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

    for i, r in enumerate(records):
        red_length = lengths_reduced[i]
        # If the length is the same, then we don't need to do anything
        if red_length >= r["length"]:
            continue

        # Otherwise, we need to truncate the text
        trunc = truncate_text_at_center(
            r["text"],
            tokenizer=tokenizer,
            max_tokens=red_length,
            allow_iterative_reduction=allow_iterative_reduction,
        )

        if trunc["text"] is None:
            trunc["text"] = ""

        if r["original_value_type"] in (int, float):
            cls_ = r["original_value_type"]

            # Let's try to convert the value back to its original type.
            # If there's a problem converting the value, then we will not change it back
            try:
                trunc["text"] = cls_(trunc["text"])
            except ValueError:
                pass

        prev_turns_lst[r["index"]][r["key"]] = trunc["text"]

    formatted = [format_output_dict_fn(turn) for turn in prev_turns_lst]

    if turn_sep is not None:
        return turn_sep.join(formatted)
    else:
        return formatted


def find_turns_with_instructor_chat(
    replay: "Replay", turn: "Turn", speaker="instructor", num_prev_turns=5
):
    """
    This looks for all the turns in `replay` up to `turn` (minus `num_prev_turns` turns)
    that are by `speaker` (default: instructor). This is used to find the instructor's utterances
    that are used as context for the current turn. The reason we have a num_prev_turns parameter
    is because we want to limit the number of turns we look at, as the last num_prev_turns turns
    can be displayed by another function, such as `format_prev_turns`, separate from this.

    This output of this function should be used by format_utterances to display the utterances.
    """
    start_index = max(0, turn.index - num_prev_turns)
    instructor_chat_turns = replay.filter_turns(
        lambda turn: turn.get("speaker") == speaker and turn.index < start_index
    )
    return instructor_chat_turns


def multi_attempt_format_prev_turns_truncated(
    replay: "Replay",
    turn: "Turn",
    format_intent,
    tokenizer: "PreTrainedTokenizer",
    max_tokens: int,
    num_prev_turns: int = 5,
    turn_sep: str = " ; ",
    max_attempts: int = 5,
    format_output_dict_fn: Callable = format_output_dictionary,
    warn_after_attempts: bool = True,
    allow_iterative_reduction=False,
):
    """
    This function behaves the same as `format_prev_turns_truncated`, but it will attempt to
    truncate the text multiple times until it fits within the `max_tokens`. This is useful
    when the object is difficult to truncate, and the function is unable to truncate the text
    using the approximation method described in the strategic truncation part of the paper.
    """
    prev_turns_tokens = tokenizer.tokenize(
        format_prev_turns_truncated(
            replay=replay,
            turn=turn,
            format_intent=format_intent,
            tokenizer=tokenizer,
            num_tokens_to_remove=0,
            num_prev_turns=num_prev_turns,
            format_output_dict_fn=format_output_dict_fn,
            turn_sep=turn_sep if turn_sep is not None else " ; ",
        ),
        add_special_tokens=False,
    )

    for _ in range(max_attempts):
        num_tokens_to_remove = len(prev_turns_tokens) - max_tokens

        prev_turns_formatted = format_prev_turns_truncated(
            replay=replay,
            turn=turn,
            format_intent=format_intent,
            tokenizer=tokenizer,
            num_tokens_to_remove=num_tokens_to_remove,
            num_prev_turns=num_prev_turns,
            format_output_dict_fn=format_output_dict_fn,
            turn_sep=turn_sep,
        )
        if isinstance(prev_turns_formatted, list):
            prev_turns_formatted_str = " ; ".join(prev_turns_formatted)
        else:
            prev_turns_formatted_str = prev_turns_formatted

        prev_turns_tokens = tokenizer.tokenize(
            prev_turns_formatted_str, add_special_tokens=False
        )

        if max_tokens is None or (len(prev_turns_tokens) <= max_tokens):
            return prev_turns_formatted

    if warn_after_attempts:
        logging.warning(
            f"Reached max # of attempts to truncate prev_turns "
            f"for demo {turn.demo_name}@{turn.index} (last: {len(prev_turns_tokens)} -> {max_tokens})"
        )

    # We will try to truncate the text directly
    if turn_sep is not None:
        trunc = truncate_text_at_center(
            prev_turns_formatted,
            tokenizer=tokenizer,
            max_tokens=max_tokens,
            allow_iterative_reduction=allow_iterative_reduction,
        )
        prev_turns_formatted = trunc["text"]
    else:
        num_turn_sep_tokens = len(tokenizer.tokenize(" ; ", add_special_tokens=False))
        # We will truncate each turn individually up to the max_tokens, removing turns
        # until we are able to fit the turns into the max_tokens

        num_tokens_remaining = max_tokens
        num_turns_remaining = num_prev_turns

        for i in range(num_prev_turns):
            trunc = truncate_text_at_center(
                prev_turns_formatted[i],
                tokenizer=tokenizer,
                max_tokens=math.ceil(num_tokens_remaining / num_turns_remaining),
                allow_iterative_reduction=allow_iterative_reduction,
            )
            prev_turns_formatted[i] = trunc["text"]
            tokens = tokenizer.tokenize(trunc["text"], add_special_tokens=False)
            num_tokens_remaining -= len(tokens) + num_turn_sep_tokens
            num_turns_remaining -= 1

    return prev_turns_formatted


def format_utterances_truncated(
    turns: List["Turn"],
    tokenizer: "PreTrainedTokenizer",
    max_tokens: int,
    format_utterances_fn,
    num_utterances: int = 5,
    type_filter="chat",
    sep=" ",
    convert_to_minutes=True,
    template="[{timestamp}] {utterance}",
    allow_iterative_reduction=False,
):
    """
    Formats utterances from a list of turns. The utterances are formatted as follows:
    1. If there are no utterances, return "No instructor utterance"
    2. If there are less than `num_utterances` utterances, return all utterances
    3. If there are more than `num_utterances` utterances, return the first and last `num_utterances-1` utterances

    If sep is None, then the utterances are returned as a list. Otherwise, they are joined by `sep`.
    """
    utterances = format_utterances_fn(
        turns,
        num_utterances=num_utterances,
        type_filter=type_filter,
        sep=None,
        convert_to_minutes=convert_to_minutes,
        template=template,
    )

    if sep is None:
        utterances_str = " ".join(utterances)
    else:
        utterances_str = str(sep).join(utterances)

    utter_tokens = tokenizer.tokenize(utterances_str, add_special_tokens=False)
    num_tokens_to_remove = len(utter_tokens) - max_tokens

    records = []
    for i, text in enumerate(utterances):
        tokens = tokenizer.tokenize(text, add_special_tokens=False)
        records.append(
            {
                "index": i,
                "text": text,
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
            rec["text"],
            tokenizer=tokenizer,
            max_tokens=red_length,
            allow_iterative_reduction=allow_iterative_reduction,
        )

        utterances[rec["index"]] = trunc["text"]

    if sep is None:
        return utterances
    else:
        return sep.join(utterances)


def find_prev_turn_with_candidates(prev_turns, candidates, reverse=True):
    """
    For a given turn and candidates for all turns, this search
    in the reverse direction to find the previous turn that has
    candidates. This is useful for chat turns, since the candidates
    are only available for browser actions; though in rare cases,
    they may also be missing in browser turns too.

    Parameters
    ----------
    prev_turns : list
        The list of previous turns to search through.

    candidates : dict
        The candidates for all turns, as a dictionary of lists.

    reverse : bool, optional
        Whether to search in the reverse direction. Defaults to True.

    Returns
    -------
    Turn
        The previous turn that has candidates, or None if no such turn is found.
    """
    if reverse:
        prev_turns = reversed(prev_turns)

    for turn in prev_turns:
        if (turn.demo_name, turn.index) in candidates:
            return turn

    return None


def select_candidates_for_turn(candidates, turn, num_candidates=20):
    """
    This will select the top candidates for the given turn. The candidates are sorted by their rank,
    and the top `num_candidates` will be returned.

    Parameters
    ----------
    candidates : dict
        The candidates for all turns, as a dictionary of lists.

    turn : Turn
        The turn to select the candidates for.

    num_candidates : int, optional
        The number of candidates to select. Defaults to 20.

    Returns
    -------
    list
        The top candidates for the given turn.
    """
    if candidates is None:
        return None

    if turn is None:
        return None

    key = (turn.demo_name, turn.index)

    if key in candidates:
        cands_turn = sorted(candidates[key], key=lambda c: c["rank"])
        # Remove duplicates by uid
        cands_turn_dedup = []
        seen = set()
        for cand in cands_turn:
            if cand["uid"] not in seen:
                cands_turn_dedup.append(cand)
                seen.add(cand["uid"])

        return cands_turn_dedup[:num_candidates]
    else:
        return None


def select_turns_and_candidates_for_prompts(
    demos,
    candidates=None,
    num_candidates=20,
):
    """
    This will select the turns that will be used for building the prompts. It first filters
    turns based on the intents that will be predicted, whether the turn has a validated
    screenshot, and if it's a chat turn, then whether the speaker is not the navigator.
    Then, we will select the candidates for each turn, and if we cannot find any candidates
    for a given turn, then we will find the previous turn that has candidates.

    Parameters
    ----------
    demos : list
        The list of demonstrations to select the turns from.

    candidates : dict, optional
        The candidates for all turns, as a dictionary of lists. If None, then the candidates
        will not be used. Defaults to None.

    num_candidates : int, optional
        The number of candidates to select for each turn. Defaults to 20.

    Returns
    -------
    list
        A list of dictionaries, where each dictionary contains the following keys:
        - replay: The replay for the turn
        - turn: The turn to use for the prompt
        - cands_turn: The candidates for the turn, or None if no candidates are found

    """
    turn_recs_for_building_prompt = []
    for demo in tqdm(demos, desc="Processing demos into input records"):
        replay = Replay.from_demonstration(demo)
        turns = replay.filter_by_intents(
            "click", "change", "textInput", "scroll", "load", "say", "submit"
        )
        for turn in turns:
            if turn.type == "chat" and not turn.has_screenshot():
                replay.assign_screenshot_to_turn(turn)

        turns = filter_turns(
            turns, lambda t: t.has_screenshot() and t.get_screenshot_status() == "good"
        )
        turns = filter_turns(
            turns,
            lambda turn: not (
                turn.type == "chat" and turn.get("speaker") != "navigator"
            ),
        )

        for i, turn in enumerate(turns):
            if candidates is None:
                cands_turn = None
            else:
                cands_turn = select_candidates_for_turn(
                    candidates, turn, num_candidates=num_candidates
                )
                # If we did not find any candidates for the current turn,
                # then we need to find the previous turn that has candidates
                if cands_turn is None:
                    prev_turn = find_prev_turn_with_candidates(
                        prev_turns=turns[:i], candidates=candidates
                    )
                    cands_turn = select_candidates_for_turn(
                        candidates, prev_turn, num_candidates=num_candidates
                    )

            if cands_turn is None:
                logging.info(
                    f"No candidates for demo: {turn.demo_name}, turn: {turn.index}, type: {turn.type}, intent: {turn.intent}"
                )

            turn_recs_for_building_prompt.append(
                dict(
                    replay=replay,
                    turn=turn,
                    cands_turn=cands_turn,
                )
            )

    return turn_recs_for_building_prompt


def build_input_record_for_single_turn(
    turn_dict,
    format_intent,
    build_prompt_records_fn,
    format_prompt_records_fn,
):
    """
    This builds the input record for a single turn. The input record is a dictionary, which contains
    the following
    - demo_name: The name of the demonstration
    - base_dir: The base directory of the demonstration
    - turn_index: The index of the turn
    - prompt: The prompt to use for the model
    - output_target: The target output for the model
    - output_target_dict: The target output for the model, but in dictionary format

    If `candidates` is not None, then the prompt includes the candidates as well.

    Parameters
    ----------
    turn_dict : dict
        A dictionary containing the following
        - replay: The replay for the turn
        - turn: The turn to use for the prompt
        - cands_turn: The candidates for the turn, or None if no candidates are found

    format_intent : Callable
        A function that takes a turn and returns a string or a dictionary.

    build_prompt_records_fn : Callable
        A function that takes a replay, turn, and cands_turn, and returns the prompt records.

    format_prompt_records_fn : Callable
        A function that takes the prompt records and formats them.

    Returns
    -------
    dict
        The input record for the model.
    """
    replay = turn_dict["replay"]
    turn = turn_dict["turn"]
    cands_turn = turn_dict["cands_turn"]

    prompt_recs = build_prompt_records_fn(
        replay=replay,
        turn=turn,
        cands_turn=cands_turn,
    )

    if format_prompt_records_fn is None:
        prompt_fmt = prompt_recs
    else:
        prompt_fmt = format_prompt_records_fn(prompt_recs)

    return {
        "demo_name": turn.demo_name,
        "base_dir": turn.base_dir,
        "turn_index": turn.index,
        "prompt": prompt_fmt,
        "output_target": format_intent(turn, return_as=str),
        "output_target_dict": format_intent(turn, return_as=dict),
        "use_candidates": cands_turn is not None,
        "screenshot_path": turn.get_screenshot_path(),
    }


def build_input_records_from_selected_turns(
    selected_turns,
    format_intent,
    build_prompt_records_fn,
    format_prompt_records_fn,
):
    """
    This will build the input records for the model. The input records are a list of dictionaries,
    which contains the following keys:
    - demo_name: The name of the demonstration
    - base_dir: The base directory of the demonstration
    - turn_index: The index of the turn
    - prompt: The prompt to use for the model
    - output_target: The target output for the model
    - output_target_dict: The target output for the model, but in dictionary format

    If `candidates` is not None, then the prompt includes the candidates as well.

    Parameters
    ----------
    selected_turns : list
        The list of selected turns to build the input records from.

    format_intent : Callable
        A function that takes a turn and returns a string or a dictionary.

    build_prompt_records_fn : Callable
        A function that takes a replay, turn, and cands_turn, and returns the prompt records.

    format_prompt_records_fn : Callable
        A function that takes the prompt records and formats them.

    Returns
    -------
    list
        A list of input records for the model.
    """
    input_records = []
    for selected_turn_dict in tqdm(selected_turns, desc="Building input records"):
        rec = build_input_record_for_single_turn(
            turn_dict=selected_turn_dict,
            format_intent=format_intent,
            build_prompt_records_fn=build_prompt_records_fn,
            format_prompt_records_fn=format_prompt_records_fn,
        )

        input_records.append(rec)

    return input_records


def build_input_records_from_selected_turns_parallel(
    selected_turns,
    format_intent,
    build_prompt_records_fn,
    format_prompt_records_fn,
    num_processes=4,
    chunksize=50,
):
    """
    This will build the input records for the model. The input records are a list of dictionaries,
    which contains the following keys:
    - demo_name: The name of the demonstration
    - base_dir: The base directory of the demonstration
    - turn_index: The index of the turn
    - prompt: The prompt to use for the model
    - output_target: The target output for the model
    - output_target_dict: The target output for the model, but in dictionary format

    If `candidates` is not None, then the prompt includes the candidates as well.
    If `num_processes` is greater than 1, then this will use multiprocessing to build the input records.

    Parameters
    ----------
    selected_turns : list
        The list of selected turns to build the input records from.

    format_intent : Callable
        A function that takes a turn and returns a string or a dictionary.

    build_prompt_records_fn : Callable
        A function that takes a replay, turn, and cands_turn, and returns the prompt records.

    format_prompt_records_fn : Callable
        A function that takes the prompt records and formats them.

    num_processes : int, optional
        The number of processes to use to build the input records. If 1, then this will use a single
        process. Defaults to 4.

    chunksize : int, optional
        The chunksize to use for multiprocessing. Defaults to 50. This allows the processes to work
        on a chunk of `chunksize` turns at a time instead of one turn at a time, allowing for better
        performance.

    Returns
    -------
    list
        A list of input records for the model.
    """
    # We want to still use tqdm to show the progress bar, so we will use the
    # multiprocessing.Pool.imap_unordered function, which returns an iterator

    func = partial(
        build_input_record_for_single_turn,
        format_intent=format_intent,
        build_prompt_records_fn=build_prompt_records_fn,
        format_prompt_records_fn=format_prompt_records_fn,
    )

    if num_processes > 1:

        pool = Pool(num_processes)
        # pool = ThreadPool(num_processes)
        iterator = pool.imap(
            func,
            selected_turns,
            chunksize=chunksize,
        )
    else:
        iterator = map(
            func,
            selected_turns,
        )

    input_records = []

    desc = f"Building input records (num_proc={num_processes})"
    total = len(selected_turns)
    for rec in tqdm(iterator, desc=desc, total=total):
        input_records.append(rec)

    return input_records
