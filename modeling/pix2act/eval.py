"""
Using the weblinx API to load each action and the associated screenshot.
"""

import json
from pathlib import Path

import datasets
import hydra
from hydra.core.hydra_config import HydraConfig
import torch
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers import (
    Pix2StructForConditionalGeneration,
    AutoTokenizer,
    Pix2StructImageProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
from transformers.models.pix2struct.image_processing_pix2struct import render_header

import weblinx as wl
from weblinx.utils.hydra import resolve_cache_path, save_path_to_hydra_logs

from .processing import (
    extract_and_format_input_and_output,
    process_sample,
)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg):
    split_path = Path(cfg.data.split_path).expanduser()
    result_dir = Path(cfg.eval.result_dir).expanduser()
    model_save_dir = Path(cfg.model.save_dir).expanduser()
    result_dir.mkdir(parents=True, exist_ok=True)
    cache_path, load_from_cache_file = resolve_cache_path(cfg)

    torch_dtype = torch.bfloat16

    # Load the model, tokenizer, and image processor
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = Pix2StructImageProcessor.from_pretrained(
        cfg.model.name, is_vqa=True, max_patches=cfg.model.max_input_patches
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.name)
    model = Pix2StructForConditionalGeneration.from_pretrained(
        model_save_dir, torch_dtype=torch_dtype
    )
    model = model.to(device).eval()

    # Data processing
    demo_names = wl.utils.load_demo_names_in_split(split_path, split=cfg.eval.split)
    demos = [wl.Demonstration(demo_name, base_dir=cfg.data.base_dir) for demo_name in demo_names]
    processed_data_records, output_records = extract_and_format_input_and_output(
        demos, return_output_records=True
    )

    torch.set_num_threads(1)  # Needed for multiprocess data processing
    train_dset = datasets.Dataset.from_list(processed_data_records)

    train_dset = train_dset.map(
        process_sample,
        fn_kwargs=dict(
            tokenizer=tokenizer,
            processor=processor,
            max_out_len=cfg.model.max_out_len,
            font_path=cfg.data.font_path,
        ),
        num_proc=cfg.data.num_proc,
        batched=True,
        batch_size=16,
        remove_columns=train_dset.column_names,
        load_from_cache_file=load_from_cache_file,
        cache_file_name=cache_path,
    )

    loader = DataLoader(
        train_dset.with_format("torch"),
        batch_size=cfg.eval.batch_size_per_device,
        num_workers=cfg.train.dataloader_num_workers,
    )

    outputs = []

    with torch.cuda.amp.autocast(dtype=torch_dtype):
        for batch in tqdm(loader, desc="Generating outputs"):
            for k in batch:
                batch[k] = batch[k].to(device)

            generated = model.generate(**batch, max_new_tokens=cfg.model.max_out_len)
            outputs.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))

    results = []
    for i, output in enumerate(outputs):
        rec = processed_data_records[i]
        d = {
            "output_predicted": output,
            "header_text": rec["header_text"],
            "output_target": rec["output_text"],
            "demo_name": rec["demo_name"],
            "turn_index": rec["turn_index"],
            "output_target_dict": output_records[i],
        }
        results.append(d)

    # Save results
    with open(result_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    save_path_to_hydra_logs(save_dir=model_save_dir)

    return results


if __name__ == "__main__":
    main()
