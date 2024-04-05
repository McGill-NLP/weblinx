from functools import partial

import weblinx.utils.format as wlf


def build_formatter_for_multichoice():
    format_click = partial(wlf.format_click, formatters=(wlf.format_uid,))
    format_text_input = partial(
        wlf.format_text_input,
        formatters=(
            partial(wlf.format_arg_item, name="text", max_length=200),
            wlf.format_uid,
        ),
    )
    format_change = partial(
        wlf.format_change,
        formatters=(
            partial(wlf.format_arg_item, name="value", max_length=200),
            wlf.format_uid,
        ),
    )
    format_submit = partial(wlf.format_submit, formatters=(wlf.format_uid,))
    format_load = partial(
        wlf.format_load,
        include_transition=False,
        include_timestamp=False,
        max_length=200,
    )
    format_scroll = partial(wlf.format_scroll, include_timestamp=False)

    format_say = partial(wlf.format_say, include_timestamp=False)

    format_intent_auto = partial(
        wlf.format_intent_automatically,
        format_change=format_change,
        format_click=format_click,
        format_load=format_load,
        format_say=format_say,
        format_scroll=format_scroll,
        format_submit=format_submit,
        format_text_input=format_text_input,
    )

    return format_intent_auto


def format_prompt_for_flan(
    input_records,
    role_name="role",
    content_name="content",
    navigator_name="Assistant",
):
    out_str = ""
    for r in input_records:
        # For system, we do not add System, since it's for a instruct model
        if r[role_name] == "system":
            out_str += r[content_name] + "\n"
        else:
            out_str += f"{r[role_name].capitalize()}: {r[content_name]}\n"

    out_str += f"\n{navigator_name}:"
    return out_str
