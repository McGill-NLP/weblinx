from functools import partial

from PIL import Image
from tqdm.auto import tqdm
import torch

import weblinx as wl
import weblinx.utils.format as wlf
from weblinx.processing.prompt import (
    format_prev_turns,
    format_utterances,
    find_turns_with_instructor_chat,
)


def format_turn_for_input(
    replay,
    turn,
    format_intent,
    turn_sep=" ; ",
    num_prev_turns=5,
    num_utterances=5,
    return_str=True,
):
    """
    This function formats a turn for input to the model. It does so by combining the following:
    1. The first and last `num_utterances-1` utterances from the instructor
    2. The previous turns (up to `num_prev_turns` turns)

    If return_str is True, then the output is a string. Otherwise, it returns two strings: the utterance context and the previous turns.

    """
    prev_turns_text = format_prev_turns(
        replay=replay,
        turn=turn,
        format_intent=format_intent,
        turn_sep=turn_sep,
        num_prev_turns=num_prev_turns,
    )
    instructor_chat_turns = find_turns_with_instructor_chat(
        replay, turn, num_prev_turns=num_prev_turns
    )
    utterance_context = format_utterances(
        instructor_chat_turns, num_utterances=num_utterances
    )

    if not return_str:
        return utterance_context, prev_turns_text

    # Now, let's combine the text from the previous turns with the utterance context
    # and the current turn's utterance
    text = (
        f"Viewport(height={turn.viewport_height}, width={turn.viewport_width}) ---- "
        f"Instructor Utterances: {utterance_context} ---- "
        f"Previous Turns:{prev_turns_text}"
    )

    return text


def build_formatters():
    format_element_input = partial(
        wlf.format_element,
        include_text=False,
        include_attrs=("class", "title", "href", "aria-label", "d", "src"),
    )
    format_click_input = partial(
        wlf.format_click,
        formatters=(wlf.format_mouse_xy, format_element_input, wlf.format_timestamp),
    )
    format_change_input = partial(
        wlf.format_change,
        formatters=(
            partial(wlf.format_arg_item, name="value"),
            format_element_input,
            wlf.format_timestamp,
        ),
    )
    format_hover_input = partial(
        wlf.format_hover,
        formatters=(wlf.format_mouse_xy, format_element_input, wlf.format_timestamp),
    )

    format_submit_input = partial(
        wlf.format_submit, formatters=(format_element_input, wlf.format_timestamp)
    )

    format_text_input_input = partial(
        wlf.format_text_input,
        formatters=(
            partial(wlf.format_arg_item, name="text"),
            partial(format_element_input),
            wlf.format_timestamp,
        ),
    )

    format_intent_input = partial(
        wlf.format_intent_automatically,
        format_click=format_click_input,
        format_change=format_change_input,
        format_hover=format_hover_input,
        format_submit=format_submit_input,
        format_text_input=format_text_input_input,
        return_as=str,
    )

    # second, for the output (prediction text)
    format_element_out = partial(
        wlf.format_element,
        # Only want the tag
        include_text=False,
        include_attrs=False,
    )

    format_click_out = partial(wlf.format_click, formatters=(wlf.format_mouse_xy,))
    format_text_input_out = partial(
        wlf.format_text_input,
        formatters=(
            partial(wlf.format_arg_item, name="text", max_length=200),
            format_element_out,
            wlf.format_target_bbox,
        ),
    )
    format_change_out = partial(
        wlf.format_change,
        formatters=(
            partial(wlf.format_arg_item, name="value", max_length=200),
            format_element_out,
            wlf.format_target_bbox,
        ),
    )
    format_submit_out = partial(
        wlf.format_submit, formatters=(format_element_out, wlf.format_target_bbox)
    )
    format_load_out = partial(
        wlf.format_load,
        include_transition=False,
        include_timestamp=False,
        max_length=200,
    )
    format_scroll_out = partial(wlf.format_scroll, include_timestamp=False)

    format_say_out = partial(wlf.format_say, include_timestamp=False)

    format_intent_out = partial(
        wlf.format_intent_automatically,
        format_change=format_change_out,
        format_click=format_click_out,
        format_load=format_load_out,
        format_say=format_say_out,
        format_scroll=format_scroll_out,
        format_submit=format_submit_out,
        format_text_input=format_text_input_out,
    )

    return format_intent_input, format_intent_out


def extract_and_format_input_and_output(demos, return_output_records=False):
    format_intent_input, format_intent_out = build_formatters()
    processed_data_records = []
    output_records = []

    for demo in tqdm(demos, desc="Extracting text from demos"):
        replay = wl.Replay.from_demonstration(demo)
        target_turns = replay.filter_by_intents(
            "click", "change", "textInput", "scroll", "load", "say", "submit"
        )
        for turn in target_turns:
            if turn.type == "chat" and not turn.has_screenshot():
                replay.assign_screenshot_to_turn(turn)

        # Filter out turns without screenshots
        target_turns = [
            turn
            for turn in target_turns
            if (turn.has_screenshot() and turn.get_screenshot_status() == "good")
        ]
        # Filter out chat turns that not by a navigator (since we do not predict instructor utterance)
        target_turns = [
            turn
            for turn in target_turns
            if not (turn.type == "chat" and turn.get("speaker") != "navigator")
        ]

        for turn in target_turns:
            image_path = turn.get_screenshot_path()

            formatted_input = format_turn_for_input(
                replay, turn, format_intent=format_intent_input
            )
            formatted_output = format_intent_out(turn, return_as=str)
            formatted_out_dict = format_intent_out(turn, return_as=dict)

            processed_data_records.append(
                {
                    "image_obj": Image.open(image_path),
                    "header_text": formatted_input,
                    "output_text": formatted_output,
                    "demo_name": demo.name,
                    "turn_index": turn.index,
                }
            )
            output_records.append(formatted_out_dict)

    if return_output_records:
        return processed_data_records, output_records
    else:
        return processed_data_records


def process_sample(sample, tokenizer, processor, max_out_len, font_path):
    out = processor(
        images=sample["image_obj"],
        header_text=sample["header_text"],
        return_tensors="pt",
        font_path=font_path,
    )
    tokens = tokenizer(
        text=sample["output_text"],
        max_length=max_out_len,
        truncation=True,
        padding="max_length",
        return_tensors="pt",
    )
    # In input_ids, replace the padding token with -100 (the ignore index)
    tokens["input_ids"][tokens["input_ids"] == tokenizer.pad_token_id] = -100
    out["labels"] = tokens["input_ids"]

    return out


def data_collator(features):
    batch = {}
    batch["labels"] = torch.tensor([f["labels"] for f in features])
    batch["flattened_patches"] = torch.tensor(
        [f["flattened_patches"] for f in features]
    )
    batch["attention_mask"] = torch.tensor([f["attention_mask"] for f in features])

    return batch
