from functools import partial
import logging
import json
from pathlib import Path

import hydra
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
import torch
from tqdm import tqdm
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    BitsAndBytesConfig,
    pipeline,
)
from transformers.pipelines.pt_utils import KeyDataset
from modeling.llama.processing import build_prompt_records_for_llama_truncated

import weblinx as wl
from weblinx.processing import load_candidate_elements
from weblinx.processing.prompt import (
    build_input_records_from_selected_turns,
    select_turns_and_candidates_for_prompts,
)
from weblinx.utils.hydra import save_path_to_hydra_logs

from .processing import (
    format_prompt_for_flan,
    build_formatter_for_multichoice,
)

from .processing_m2w import build_formatter_for_m2w, build_prompt_records_for_m2w


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg):
    logger = logging.getLogger(__name__)

    split_path = Path(cfg.data.split_path).expanduser()
    result_dir = Path(cfg.eval.result_dir).expanduser()
    model_save_dir = Path(cfg.model.save_dir).expanduser()

    max_out_len = cfg.model.max_out_len
    split = cfg.eval.split

    result_dir.mkdir(parents=True, exist_ok=True)

    logger.info(OmegaConf.to_yaml(cfg))

    candidates = load_candidate_elements(path=cfg.candidates.path)

    tokenizer = AutoTokenizer.from_pretrained(cfg.model.tokenizer)
    if cfg.model.max_inp_len is not None:
        tokenizer.model_max_length = cfg.model.max_inp_len

    # Data loading
    demo_names = wl.utils.load_demo_names_in_split(split_path, split=split)
    demos = [wl.Demonstration(name) for name in demo_names]

    if cfg.data.use_m2w:
        format_intent = build_formatter_for_m2w()
        build_prompt_records_fn = partial(
            build_prompt_records_for_m2w,
            format_intent=format_intent,
        )

    else:
        build_prompt_records_fn = partial(
            build_prompt_records_for_llama_truncated,
            format_intent=format_intent,
            tokenizer=tokenizer,
        )

    format_intent = build_formatter_for_multichoice()

    selected_turns = select_turns_and_candidates_for_prompts(
        demos=demos,
        candidates=candidates,
        num_candidates=cfg.candidates.k,
    )

    input_records = build_input_records_from_selected_turns(
        selected_turns=selected_turns,
        format_intent=format_intent,
        build_prompt_records_fn=build_prompt_records_fn,
        format_prompt_records_fn=format_prompt_for_flan,
    )

    model_kwargs = dict(device_map="auto", torch_dtype=torch.bfloat16)

    if cfg.eval.get("load_from_save_dir", False) is True:
        model_load_name = str(model_save_dir)
    else:
        model_load_name = cfg.model.name

    model = AutoModelForSeq2SeqLM.from_pretrained(model_load_name, **model_kwargs)

    dset = KeyDataset(input_records, key="prompt")
    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
    )
    pipe_kwargs = dict(
        max_new_tokens=max_out_len,
        batch_size=cfg.eval.batch_size_per_device,
        pad_token_id=tokenizer.eos_token_id,
        truncation=True if cfg.model.max_inp_len is not None else False,
    )

    results = []

    with torch.cuda.amp.autocast(dtype=torch.bfloat16):
        pbar = tqdm(
            pipe(dset, **pipe_kwargs), desc="Generating outputs", total=len(dset)
        )
        for i, out in enumerate(pbar):
            rec = input_records[i]
            generated_text = out[0]["generated_text"]
            result = {
                "demo_name": rec["demo_name"],
                "turn_index": rec["turn_index"],
                "prompt": rec["prompt"],
                "output_predicted": generated_text,
                "output_target": rec["output_target"],
                "output_target_dict": rec["output_target_dict"],
            }

            results.append(result)

    # Save results
    with open(result_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    save_path_to_hydra_logs(save_dir=result_dir)


if __name__ == "__main__":
    main()
