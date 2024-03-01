---
title: "Processing"
permalink: /docs/processing/
toc_label: "Table of Contents"
layout: single
---
## Reference for `weblinx.processing`

### `load_candidate_elements`

```
weblinx.processing.load_candidate_elements(path, group_keys=('"demo_name"', '"turn_index"'), log_fn=None)
```

#### Description

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


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `path` | `str` |  | The path to the candidates file. This can be a JSONL file. |
| `group_keys` | `tuple[str]` | `('"demo_name"', '"turn_index"')` | The keys to use to group the candidates. If None, then the candidates will not be grouped. |


#### Returns

```
list or dict
```

The candidates, either as a list or as a dictionary of lists.

#### Example

Here's an example of how to use this function:
```
candidates = load_candidate_elements("candidates.jsonl", group_keys=("demo_name", "turn_index"))
```

This will load the candidates from the file "candidates.jsonl" and group them by the keys "demo_name"
and "turn_index". The candidates will be returned as a dictionary of lists.

## Reference for `weblinx.processing.dom`

### `get_tree_repr_simple`

```
weblinx.processing.dom.get_tree_repr_simple(tree, keep_html_brackets=False, copy=True, postfix="\nAbove are the pruned HTML contents of the page.")
```

#### Description

    This will return a simple representation of the tree in a string format.
    This is useful if you want to pass the tree to a action model like a LLM, which
    can only accept strings (and images in the case of multimodal models).

    Parameters
    ----------
    tree : lxml.html.HtmlElement
        The tree to get the representation of.
    keep_html_brackets : bool, optional
        Whether to keep the HTML brackets or not. Defaults to False.
    copy : bool, optional
        Whether to copy the tree or not. Defaults to True.
    postfix : str, optional
        A string to append to the end of the tree representation. Defaults to "
Above are the pruned HTML contents of the page.".

    Returns
    -------
    str
        The string representation of the tree.

    Raises
    ------
    ImportError
        If the lxml library is not installed.

    Note
    ----
    This function is based on the works of Mind2Web (@xiang-deng). Copyrights belong
    to the original author. The original code can be found here at osu-nlp-group/mind2web
    

### `sanitize_elem_attributes`

```
weblinx.processing.dom.sanitize_elem_attributes(tree, remove_data_attrs=True, remove_underscore_attrs=True, remove_angular_attrs=True, remove_alpine_attrs=True, remove_xml_attrs=True, remove_google_attrs=True, remove_id_attrs=True, uid_key="data-webtasks-id")
```

#### Description

This will take a tree and sanitize the attributes of the elements.
This is needed in order to remove any attributes that are not needed before the
element selection stage of the ranking model.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `tree` | `lxml.html.HtmlElement` |  | The tree to sanitize. |
| `remove_data_attrs` | `bool` | `True` | Whether to remove data- attributes or not. Defaults to True. |
| `remove_underscore_attrs` | `bool` | `True` | Whether to remove _ attributes or not. Defaults to True. |
| `remove_angular_attrs` | `bool` | `True` | Whether to remove ng attributes or not. Defaults to True. |
| `remove_alpine_attrs` | `bool` | `True` | Whether to remove x- attributes or not. Defaults to True. |
| `remove_xml_attrs` | `bool` | `True` | Whether to remove xml attributes or not. Defaults to True. |
| `remove_google_attrs` | `bool` | `True` | Whether to remove js attributes or not. Defaults to True. |
| `remove_id_attrs` | `bool` | `True` | Whether to remove id attributes or not. Defaults to True. |
| `uid_key` | `str` | `"data-webtasks-id"` | The key to use as the unique identifier. Defaults to "data-webtasks-id". |


#### Raises

ImportError
    If the lxml library is not installed.

### `remove_uid_when_not_candidate`

```
weblinx.processing.dom.remove_uid_when_not_candidate(dom_tree, candidate_uids, uid_key="data-webtasks-id")
```

#### Description

This will remove the uid from the tree if it is not in the candidate_uids. This is
useful for removing any uids that are not in the candidate set.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `dom_tree` | `lxml.html.HtmlElement` |  | The tree to remove the uids from. |
| `candidate_uids` | `list` |  | The list of candidate uids to keep. |
| `uid_key` | `str` | `"data-webtasks-id"` | The key to use as the unique identifier. Defaults to "data-webtasks-id". |


#### Raises

ImportError
    If the lxml library is not installed.

### `remove_html_comments`

```
weblinx.processing.dom.remove_html_comments(dom_tree)
```

#### Description

Will try to remove all HTML comments from the tree.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `dom_tree` | `lxml.html.HtmlElement` |  | The tree to remove the comments from. |


### `get_descendants`

```
weblinx.processing.dom.get_descendants(node, max_depth, current_depth=0)
```

#### Description

This function was originally written by @xiang-deng for the [mind2web repository](https://github.com/OSU-NLP-Group/Mind2Web/blob/3740087ab004fe98a117f6261cb1937dfc9fa66e/src/data_utils/dom_utils.py)

It is kept as is and added here for convenience. All copyrights belong to the original author.

### `prune_tree`

```
weblinx.processing.dom.prune_tree(dom_tree, candidate_set, max_depth=5, max_children=50, max_sibling=3, uid_key="data-webtasks-id")
```

#### Description

This function was originally written by @xiang-deng for the [mind2web repository](https://github.com/OSU-NLP-Group/Mind2Web/blob/3740087ab004fe98a117f6261cb1937dfc9fa66e/src/data_utils/dom_utils.py#L203)

It was modified to allow uid_key to be specified. All rights belong to the original author.

### `clean_and_prune_tree`

```
weblinx.processing.dom.clean_and_prune_tree(dom_tree, cands_turn, max_depth=1, max_children=5, max_sibling=2)
```

#### Description

This function will clean and prune the tree based on the candidates in the cands_turn. This
is useful for removing any elements that are not candidates, and for removing any elements
that are not needed for the ranking model.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `dom_tree` | `lxml.html.HtmlElement` |  | The tree to clean and prune. |
| `cands_turn` | `list` |  | The list of candidates for the turn. |
| `max_depth` | `int` | `1` | The maximum depth to prune the tree. Defaults to 1. |
| `max_children` | `int` | `5` | The maximum number of children to keep for each candidate. Defaults to 5. |
| `max_sibling` | `int` | `2` | The maximum number of siblings to keep for each candidate. Defaults to 2. |


#### Returns

```
lxml.html.HtmlElement
```

The cleaned and pruned tree.

#### Raises

ValueError
    If cands_turn is None.

## Reference for `weblinx.processing.intent`

#### `Intent.from_string`

```
weblinx.processing.intent.Intent.from_string(cls, intent)
```

#### `Intent.get_element_intents`

```
weblinx.processing.intent.Intent.get_element_intents(cls, as_set=False)
```

#### `Intent.get_text_intents`

```
weblinx.processing.intent.Intent.get_text_intents(cls, as_set=False)
```

#### `Intent.get_tab_intents`

```
weblinx.processing.intent.Intent.get_tab_intents(cls, as_set=False)
```

#### `Intent.get_eval_intents`

```
weblinx.processing.intent.Intent.get_eval_intents(cls, as_set=False)
```

## Reference for `weblinx.processing.outputs`

### `are_not_none`

```
weblinx.processing.outputs.are_not_none()
```

### `cast_to_float`

```
weblinx.processing.outputs.cast_to_float(value)
```

#### Description

Checks if a value is an int or a float.

### `format_action_arg_value`

```
weblinx.processing.outputs.format_action_arg_value(arg_value)
```

### `list_all_non_alphanum_chars`

```
weblinx.processing.outputs.list_all_non_alphanum_chars(other_chars_allowed=None)
```

#### Description

Returns a list of all non-alphanumeric characters in Python.

### `split_by_comma`

```
weblinx.processing.outputs.split_by_comma(string, check_quotes=False)
```

#### Description

This function splits a string by commas, but ignores commas inside quotes.
For example, if my string is 'a, b, "c, d", e', then this function will return
['a', 'b', '"c, d"', 'e'] if check_quotes is True, but ['a', 'b', '"c', 'd"', 'e']
if check_quotes is False.


#### Example

```python
# Let's test the function
test_string = 'a, b, "c, d", e'
print(split_by_comma(test_string, check_quotes=True))
print(split_by_comma(test_string, check_quotes=False))
```

### `find_last_non_alphanum_char`

```
weblinx.processing.outputs.find_last_non_alphanum_char(s, other_chars_allowed=None)
```

#### Description

Given a string and a list of characters, find the last index of a non-alphanumeric character in the string.

### `find_intent_and_raw_args`

```
weblinx.processing.outputs.find_intent_and_raw_args(raw_output_string)
```

#### Description

This iterative function will walk through a raw string that might contain an action
in the form `intent(arg1="val1", arg2=num1, ...)` and return the intent and the unparsed args

### `parse_predicted_output_string`

```
weblinx.processing.outputs.parse_predicted_output_string(raw_output_string)
```

#### Description

Given an output string, try to find a substring of format <intent>(<key1>=<value1>, <key2>=<value2>, ...) and return a dictionary of format:
{
    "intent": <intent>,
    "key1": <value1>,
    "key2": <value2>,
    ...
}
Returns None if the parsing fails.

### `get_element_info`

```
weblinx.processing.outputs.get_element_info(turn, uid, uid_key="data-webtasks-id", cache_dir=".cache/demonstrations/xpaths")
```

#### Description

Given a uid_key for an element, retrieve additional information about the element from the HTML which can be used for evaluation.

Extracts only the information needed for evaluation.

### `get_element_uid_by_coords`

```
weblinx.processing.outputs.get_element_uid_by_coords(turn, x, y)
```

#### Description

Given (x,y) coordinates for an element, find the smallest non-zero-sized element that contains the coordinates using bboxes and return its id.

### `get_xy_coords_corners`

```
weblinx.processing.outputs.get_xy_coords_corners(args)
```

### `dict_has_keys`

```
weblinx.processing.outputs.dict_has_keys(d, keys)
```

#### Description

Checks if a dictionary has all the keys in a list.

### `infer_element_for_action`

```
weblinx.processing.outputs.infer_element_for_action(intent, args, turn, uid_key="data-webtasks-id")
```

#### Description

Given an intent and args, infer the element that the action is performed on, if
the element is not explicitly specified.

### `extract_action_from_turn`

```
weblinx.processing.outputs.extract_action_from_turn(turn, uid_key="data-webtasks-id")
```

#### Description

Creates an action from a turn in a demonstration (i.e. the ground truth action).

### `sanitize_args`

```
weblinx.processing.outputs.sanitize_args(args)
```

#### Description

This function is used to sanitize the arguments of an action.

### `check_pred_is_suitable`

```
weblinx.processing.outputs.check_pred_is_suitable(pred)
```

#### Description

Given a prediction, check if it is suitable for evaluation.

## Reference for `weblinx.processing.prompt`

### `get_speaker`

```
weblinx.processing.prompt.get_speaker(utterance, instructor_name="User", navigator_name="Assistant", default_name=None)
```

#### Description

This will return the speaker for the utterance. If the utterance does not start with "say",
then it will return the navigator's name. If the utterance starts with "say", then it will
return the instructor's name if the speaker is "instructor", and the navigator's name if the
speaker is "navigator". If the speaker is neither "instructor" nor "navigator", then it will
return the default name, if it is not None. If the default name is None, then it will raise
a ValueError.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `utterance` | `str` |  | The utterance to get the speaker for. |
| `instructor_name` | `str` | `"User"` | The name of the instructor. Defaults to "User". |
| `navigator_name` | `str` | `"Assistant"` | The name of the navigator. Defaults to "Assistant". |
| `default_name` | `str` | `None` | The default name to use if the speaker is neither "instructor" nor "navigator". If None, then it will raise a ValueError. Defaults to None. |


#### Returns

```
str
```

The speaker for the utterance.

### `identity`

```
weblinx.processing.prompt.identity(x)
```

#### Description

Simply returns the input. Needed for the `format_intent` parameter in `format_prev_turns_truncated`.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `x` | `any` |  | The input to return. |


#### Returns

```
any
```

The input.

### `format_prev_turns`

```
weblinx.processing.prompt.format_prev_turns(replay, turn, format_intent, turn_sep=" ; ", num_prev_turns=5)
```

#### Description

Formats the previous turns (up until but not including `turn`) as a string, or as
a list if turn_sep is `None`. The previous turns are formatted using the `format_intent`
which is a function that takes a turn and returns a string or a dictionary. This function
is useful for displaying the previous turns as context for the current turn. This information
is used by the action model to predict the next action.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `replay` | `Replay` |  | The replay to get the previous turns from. |
| `turn` | `Turn` |  | The turn to get the previous turns for. |
| `format_intent` | `Callable` |  | A function that takes a turn and returns a string or a dictionary. |
| `turn_sep` | `str` | `" ; "` | The separator to use for joining the previous turns. If None, then the previous turns are returned as a list. Defaults to " ; ". |
| `num_prev_turns` | `int` | `5` | The number of previous turns to include. Defaults to 5. |


#### Returns

```
str or list
```

The previous turns formatted as a string, or as a list if turn_sep is None.

### `format_candidates`

```
weblinx.processing.prompt.format_candidates(candidates, max_char_len=300, use_uid_as_rank=False)
```

#### Description

This will format the candidates as a string. The candidates are formatted as follows:
1. If there are no candidates, return ""
2. If there are candidates, return the candidates as a string, with the rank (e.g. uid) and document (text representation of the candidate)
3. If the document is longer than `max_char_len`, then it will be truncated to `max_char_len`


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `candidates` | `list` |  | The candidates to format. |
| `max_char_len` | `int` | `300` | The maximum character length for the document. If the document is longer than this, then it will be truncated to this length. Defaults to 300. |
| `use_uid_as_rank` | `bool` | `False` | Whether to use the UID as the rank. If False, then it will use the rank from the candidates. Defaults to False. |


#### Returns

```
str
```

The candidates formatted as a string.

### `format_utterances`

```
weblinx.processing.prompt.format_utterances(turns, num_utterances=5, type_filter="chat", sep=" ", convert_to_minutes=True, template="[{timestamp}] {utterance}")
```

#### Description

Formats utterances from a list of turns. The utterances are formatted as follows:
1. If there are no utterances, return "No instructor utterance"
2. If there are less than `num_utterances` utterances, return all utterances
3. If there are more than `num_utterances` utterances, return the first and last `num_utterances-1` utterances

If sep is None, then the utterances are returned as a list. Otherwise, they are joined by `sep`.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turns` | `list` |  | The list of turns to get the utterances from. |
| `num_utterances` | `int` | `5` | The number of utterances to include. Defaults to 5. |
| `type_filter` | `str` | `"chat"` | The type of turn to include. If None, then it will include all types. Defaults to "chat". |
| `sep` | `str` | `" "` | The separator to use for joining the utterances. If None, then the utterances are returned as a list. Defaults to " ". |
| `convert_to_minutes` | `bool` | `True` | Whether to convert the timestamp to minutes. Defaults to True. |
| `template` | `str` | `"[{timestamp}] {utterance}"` | The template to use for formatting the utterances. Defaults to "[{timestamp}] {utterance}". |


#### Returns

```
str or list
```

The utterances formatted as a string, or as a list if sep is None.

### `format_prev_turns_truncated`

```
weblinx.processing.prompt.format_prev_turns_truncated(replay, turn, format_intent, tokenizer, num_tokens_to_remove, format_output_dict_fn=<_ast.Name object at 0x7feace0b3f40>, num_prev_turns=5, turn_sep=" ; ", allow_iterative_reduction=False)
```

#### Description

This performs the same function as `format_prev_turns`, but it truncates the text
to fit within the `max_tokens`. The truncation is not a regular truncation, instead
it uses the `truncate_text_at_center` function (see strategic trunction part
in the paper).

### `find_turns_with_instructor_chat`

```
weblinx.processing.prompt.find_turns_with_instructor_chat(replay, turn, speaker="instructor", num_prev_turns=5)
```

#### Description

This looks for all the turns in `replay` up to `turn` (minus `num_prev_turns` turns)
that are by `speaker` (default: instructor). This is used to find the instructor's utterances
that are used as context for the current turn. The reason we have a num_prev_turns parameter
is because we want to limit the number of turns we look at, as the last num_prev_turns turns
can be displayed by another function, such as `format_prev_turns`, separate from this.

This output of this function should be used by format_utterances to display the utterances.

### `multi_attempt_format_prev_turns_truncated`

```
weblinx.processing.prompt.multi_attempt_format_prev_turns_truncated(replay, turn, format_intent, tokenizer, max_tokens, num_prev_turns=5, turn_sep=" ; ", max_attempts=5, format_output_dict_fn=<_ast.Name object at 0x7feace024dc0>, warn_after_attempts=True, allow_iterative_reduction=False)
```

#### Description

This function behaves the same as `format_prev_turns_truncated`, but it will attempt to
truncate the text multiple times until it fits within the `max_tokens`. This is useful
when the object is difficult to truncate, and the function is unable to truncate the text
using the approximation method described in the strategic truncation part of the paper.

### `format_utterances_truncated`

```
weblinx.processing.prompt.format_utterances_truncated(turns, tokenizer, max_tokens, format_utterances_fn, num_utterances=5, type_filter="chat", sep=" ", convert_to_minutes=True, template="[{timestamp}] {utterance}", allow_iterative_reduction=False)
```

#### Description

Formats utterances from a list of turns. The utterances are formatted as follows:
1. If there are no utterances, return "No instructor utterance"
2. If there are less than `num_utterances` utterances, return all utterances
3. If there are more than `num_utterances` utterances, return the first and last `num_utterances-1` utterances

If sep is None, then the utterances are returned as a list. Otherwise, they are joined by `sep`.

### `find_prev_turn_with_candidates`

```
weblinx.processing.prompt.find_prev_turn_with_candidates(prev_turns, candidates, reverse=True)
```

#### Description

For a given turn and candidates for all turns, this search
in the reverse direction to find the previous turn that has
candidates. This is useful for chat turns, since the candidates
are only available for browser actions; though in rare cases,
they may also be missing in browser turns too.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `prev_turns` | `list` |  | The list of previous turns to search through. |
| `candidates` | `dict` |  | The candidates for all turns, as a dictionary of lists. |
| `reverse` | `bool` | `True` | Whether to search in the reverse direction. Defaults to True. |


#### Returns

```
Turn
```

The previous turn that has candidates, or None if no such turn is found.

### `select_candidates_for_turn`

```
weblinx.processing.prompt.select_candidates_for_turn(candidates, turn, num_candidates=20)
```

#### Description

This will select the top candidates for the given turn. The candidates are sorted by their rank,
and the top `num_candidates` will be returned.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `candidates` | `dict` |  | The candidates for all turns, as a dictionary of lists. |
| `turn` | `Turn` |  | The turn to select the candidates for. |
| `num_candidates` | `int` | `20` | The number of candidates to select. Defaults to 20. |


#### Returns

```
list
```

The top candidates for the given turn.

### `select_turns_and_candidates_for_prompts`

```
weblinx.processing.prompt.select_turns_and_candidates_for_prompts(demos, candidates=None, num_candidates=20)
```

#### Description

This will select the turns that will be used for building the prompts. It first filters
turns based on the intents that will be predicted, whether the turn has a validated
screenshot, and if it's a chat turn, then whether the speaker is not the navigator.
Then, we will select the candidates for each turn, and if we cannot find any candidates
for a given turn, then we will find the previous turn that has candidates.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `demos` | `list` |  | The list of demonstrations to select the turns from. |
| `candidates` | `dict` | `None` | The candidates for all turns, as a dictionary of lists. If None, then the candidates will not be used. Defaults to None. |
| `num_candidates` | `int` | `20` | The number of candidates to select for each turn. Defaults to 20. |


#### Returns

```
list
```

A list of dictionaries, where each dictionary contains the following keys:
- replay: The replay for the turn
- turn: The turn to use for the prompt
- cands_turn: The candidates for the turn, or None if no candidates are found

### `build_input_record_for_single_turn`

```
weblinx.processing.prompt.build_input_record_for_single_turn(turn_dict, format_intent, build_prompt_records_fn, format_prompt_records_fn)
```

#### Description

This builds the input record for a single turn. The input record is a dictionary, which contains
the following
- demo_name: The name of the demonstration
- base_dir: The base directory of the demonstration
- turn_index: The index of the turn
- prompt: The prompt to use for the model
- output_target: The target output for the model
- output_target_dict: The target output for the model, but in dictionary format

If `candidates` is not None, then the prompt includes the candidates as well.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `turn_dict` | `dict` |  | A dictionary containing the following - replay: The replay for the turn - turn: The turn to use for the prompt - cands_turn: The candidates for the turn, or None if no candidates are found |
| `format_intent` | `Callable` |  | A function that takes a turn and returns a string or a dictionary. |
| `build_prompt_records_fn` | `Callable` |  | A function that takes a replay, turn, and cands_turn, and returns the prompt records. |
| `format_prompt_records_fn` | `Callable` |  | A function that takes the prompt records and formats them. |


#### Returns

```
dict
```

The input record for the model.

### `build_input_records_from_selected_turns`

```
weblinx.processing.prompt.build_input_records_from_selected_turns(selected_turns, format_intent, build_prompt_records_fn, format_prompt_records_fn)
```

#### Description

This will build the input records for the model. The input records are a list of dictionaries,
which contains the following keys:
- demo_name: The name of the demonstration
- base_dir: The base directory of the demonstration
- turn_index: The index of the turn
- prompt: The prompt to use for the model
- output_target: The target output for the model
- output_target_dict: The target output for the model, but in dictionary format

If `candidates` is not None, then the prompt includes the candidates as well.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `selected_turns` | `list` |  | The list of selected turns to build the input records from. |
| `format_intent` | `Callable` |  | A function that takes a turn and returns a string or a dictionary. |
| `build_prompt_records_fn` | `Callable` |  | A function that takes a replay, turn, and cands_turn, and returns the prompt records. |
| `format_prompt_records_fn` | `Callable` |  | A function that takes the prompt records and formats them. |


#### Returns

```
list
```

A list of input records for the model.

### `build_input_records_from_selected_turns_parallel`

```
weblinx.processing.prompt.build_input_records_from_selected_turns_parallel(selected_turns, format_intent, build_prompt_records_fn, format_prompt_records_fn, num_processes=4, chunksize=50)
```

#### Description

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


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `selected_turns` | `list` |  | The list of selected turns to build the input records from. |
| `format_intent` | `Callable` |  | A function that takes a turn and returns a string or a dictionary. |
| `build_prompt_records_fn` | `Callable` |  | A function that takes a replay, turn, and cands_turn, and returns the prompt records. |
| `format_prompt_records_fn` | `Callable` |  | A function that takes the prompt records and formats them. |
| `num_processes` | `int` | `4` | The number of processes to use to build the input records. If 1, then this will use a single process. Defaults to 4. |
| `chunksize` | `int` | `50` | The chunksize to use for multiprocessing. Defaults to 50. This allows the processes to work on a chunk of `chunksize` turns at a time instead of one turn at a time, allowing for better performance. |


#### Returns

```
list
```

A list of input records for the model.

## Reference for `weblinx.processing.truncation`

### `get_bracket_length`

```
weblinx.processing.truncation.get_bracket_length(elem_open_bracket, elem_close_bracket, tokenizer)
```

#### Description

This function calculates the length of the brackets.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `elem_open_bracket` | `str` |  | The opening bracket. For example, "<" or "[". |
| `elem_close_bracket` | `str` |  | The closing bracket. For example, ">" or "]". |
| `tokenizer` | `transformers.PreTrainedTokenizer (PreTrainedTokenizer)` |  | The tokenizer to use to tokenize the brackets. This is used to calculate the length of the brackets. |


#### Returns

```
int
```

The length of the brackets.

### `reduce_list_of_lengths`

```
weblinx.processing.truncation.reduce_list_of_lengths(lengths, max_length, assert_exactly_max=True)
```

#### Description

Given a list of lengths, reduce the lengths to a maximum length. To learn more
about how this is achieved, please read the strategic truncation section in the
paper.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `lengths` | `list` |  | A list of lengths to reduce. |
| `max_length` | `int` |  | The maximum length to reduce the list of lengths to. |
| `assert_exactly_max` | `bool` | `True` | If True, then we will assert that the total length of the reduced list of lengths is exactly equal to max_length. Defaults to True. If False, then we will not assert this condition. |


#### Returns

```
list
```

The reduced list of lengths.

#### Raises

ValueError
    If the difference between the new total length and the max_length is negative.

AssertionError
    If assert_exactly_max is True and the total length of the reduced list of lengths
    is not exactly equal to max_length. Also, if the lengths are not monotonically
    increasing (i.e., the lengths are not sorted by length).

### `get_truncation_offsets`

```
weblinx.processing.truncation.get_truncation_offsets(tokens, length, num_tokens_to_remove)
```

#### Description

This calculates the start and end offsets of the tokens to remove. This is a
helper function for `truncate_text_at_center`.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `tokens` | `dict` |  | The tokens to truncate. This should be a dictionary with the keys "input_ids" and "offset_mapping". |
| `length` | `int` |  | The length of the tokens. |
| `num_tokens_to_remove` | `int` |  | The number of tokens to remove from the tokens. |


#### Returns

```
tuple
```

A tuple of the start and end offsets of the tokens to remove.

### `truncate_text_at_center`

```
weblinx.processing.truncation.truncate_text_at_center(text, tokenizer, tokens=None, max_tokens=10, ellipsis="...", ellipsis_length=None, assert_max_tokens=False, allow_retry_without_ellipsis=True, allow_iterative_reduction=False)
```

#### Description



#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `allow_iterative_reduction` | `bool` | `False` | If True, then we will allow the iterative reduction to continue until the max_tokens is reached. This is useful when the tokenizer output does not necessarily decrease when we remove tokens from the input. For example, if we remove a token that is part of a word, but the updated text is retokenized to the same number of tokens, then we will continue to remove tokens until we reach the max_tokens limit. |


### `build_records_of_tokens_for_dom_tree`

```
weblinx.processing.truncation.build_records_of_tokens_for_dom_tree(dom_tree, tokenizer, sorted_by_length=True)
```

### `truncate_dom_tree`

```
weblinx.processing.truncation.truncate_dom_tree(dom_tree, tokenizer, num_tokens_to_remove, ellipsis="...", remove_when_none=True, copy=True, allow_iterative_reduction=False)
```

#### Description

This function takes a dom tree and truncate it based on the number of tokens to remove.
It is not guaranteed that the resulting dom tree will have the exact number of tokens
as specified, but it will be close to the specified number of tokens. Please see
`multi_attempt_truncate_dom_tree` for a more robust approach.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `dom_tree` | `lxml.html.HtmlElement` |  | The dom tree to truncate. |
| `tokenizer` | `transformers.PreTrainedTokenizer (PreTrainedTokenizer)` |  | The tokenizer to use to tokenize the text. |
| `num_tokens_to_remove` | `int` |  | The number of tokens to remove from the dom tree. |
| `ellipsis` | `str` | `"..."` | The ellipsis to use to indicate that the text has been truncated. Defaults to "...". |
| `remove_when_none` | `bool` | `True` | If True, then we will remove the attribute if the value is None. Defaults to True. |
| `copy` | `bool` | `True` | If True, then we will copy the dom_tree before modifying it. Defaults to True. |
| `allow_iterative_reduction` | `bool` | `False` | If True, then we will allow the iterative reduction to continue until the max_tokens is reached. This is useful when the tokenizer output does not necessarily decrease when we remove tokens from the input. For example, if we remove a token that is part of a word, but the updated text is retokenized to the same number of tokens, then we will continue to remove tokens until we reach the max_tokens limit. |


#### Returns

```
lxml.html.HtmlElement
```

The truncated dom tree.

### `multi_attempt_truncate_dom_tree`

```
weblinx.processing.truncation.multi_attempt_truncate_dom_tree(dom_tree, tokenizer, ellipsis="...", max_attempts=5, max_tokens=700, warn_after_attempts=True, copy_tree=True, compute_final_num_tokens=False, allow_iterative_reduction=False)
```

#### Description

"
This will attempt to truncate the dom_tree to the specified number of tokens.
THe reason we need more than one attempt is because when we specify a number
of tokens to remove based on a max_tokens value, the resulting number of tokens
may be greater than the max_tokens value, due to how tokenizers work. Therefore,
we need to try multiple times to truncate the dom_tree to the specified number.
If after max_attempts, we are still unable to truncate the dom_tree to the
specified number of tokens, then we will truncate the resulting text directly.

### `convert_elem_dict_to_str`

```
weblinx.processing.truncation.convert_elem_dict_to_str(elem_dict, remove_empty=False)
```

#### Description

Convert an element dictionary to a string.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `elem_dict` | `dict` |  | The element dictionary. |
| `remove_empty` | `bool` | `False` | If True, then we will remove any empty elements. Defaults to False. |


#### Returns

```
str
```

The string representation of the element dictionary.

### `truncate_cands_turn`

```
weblinx.processing.truncation.truncate_cands_turn(cands_turn, tokenizer, num_tokens_to_remove, protected_elem_keys=('"tag"', '"bbox"'), copy=True, remove_empty=True, allow_iterative_reduction=False)
```

#### Description

This truncates the candidates turn to the specified number of tokens. This is useful
when the candidates turn is too long, and we need to truncate it to fit within the
maximum token length.


#### Parameters

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `cands_turn` | `list` |  | The candidates turn to truncate. |
| `tokenizer` | `transformers.PreTrainedTokenizer (PreTrainedTokenizer)` |  | Th tokenizer to use to tokenize the text. |
| `num_tokens_to_remove` | `int` |  | The number of tokens to remove from the candidates turn. |
| `protected_elem_keys` | `tuple` | `('"tag"', '"bbox"')` | The keys to protect from truncation. Defaults to ("tag", "bbox"). |
| `copy` | `bool` | `True` | If True, then we will copy the candidates turn before modifying it. Defaults to True. |
| `remove_empty` | `bool` | `True` | If True, then we will remove any empty elements. Defaults to True. |
| `allow_iterative_reduction` | `bool` | `False` | If True, then we will allow the iterative reduction to continue until the max_tokens is reached. This is useful when the tokenizer output does not necessarily decrease when we remove tokens from the input. For example, if we remove a token that is part of a word, but the updated text is retokenized to the same number of tokens, then we will continue to remove tokens until we reach the max_tokens limit. |


#### Returns

```
list
```

The truncated candidates turn.

### `multi_attempt_truncate_cands_turn`

```
weblinx.processing.truncation.multi_attempt_truncate_cands_turn(cands_turn, tokenizer, max_tokens, format_candidates_fn, max_attempts=5, warn_after_attempts=True, protected_elem_keys=('"tag"', '"bbox"'), allow_iterative_reduction=False)
```

#### Description

This is a more robust version of `truncate_cands_turn`. It will attempt to truncate
the candidates turn to the specified number of tokens. If after max_attempts, we are
still unable to truncate the candidates turn to the specified number of tokens, then
we will truncate the resulting text directly, as a last resort.

