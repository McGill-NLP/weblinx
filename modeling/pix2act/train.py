"""
Using the weblinx API to load each action and the associated screenshot.
"""

import logging
from pathlib import Path

import datasets
import hydra
from hydra.core.hydra_config import HydraConfig
import torch
from transformers import (
    Pix2StructForConditionalGeneration,
    AutoTokenizer,
    Pix2StructImageProcessor,
    Trainer,
    TrainingArguments,
)

import weblinx as wl
from weblinx.utils import set_seed
from weblinx.utils.hydra import resolve_cache_path, save_path_to_hydra_logs
from .processing import (
    extract_and_format_input_and_output,
    process_sample,
    data_collator,
)


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg):
    set_seed(cfg.seed)

    split_path = Path(cfg.data.split_path).expanduser()
    model_save_dir = Path(cfg.model.save_dir).expanduser()
    hydra_path = HydraConfig.get().runtime.output_dir
    logging_dir = Path(hydra_path) / "logs"
    cache_path, load_from_cache_file = resolve_cache_path(cfg)

    # Create dirs
    logging_dir.mkdir(parents=True, exist_ok=True)
    model_save_dir.mkdir(parents=True, exist_ok=True)

    # Load the model, tokenizer, and image processor
    processor = Pix2StructImageProcessor.from_pretrained(
        cfg.model.name, is_vqa=True, max_patches=cfg.model.max_input_patches
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.name)
    model = Pix2StructForConditionalGeneration.from_pretrained(cfg.model.name)

    # Data processing
    demo_names = wl.utils.load_demo_names_in_split(split_path, split=cfg.train.split)
    demos = [wl.Demonstration(demo_name) for demo_name in demo_names]
    processed_data_records = extract_and_format_input_and_output(demos)

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
    train_dset = train_dset.shuffle(seed=cfg.seed)

    # Create the training arguments and trainer, then train the model
    args = TrainingArguments(
        evaluation_strategy="no",
        save_strategy="no",
        optim=cfg.train.optim,
        learning_rate=cfg.train.learning_rate,
        per_device_train_batch_size=cfg.train.batch_size_per_device,
        per_device_eval_batch_size=cfg.train.batch_size_per_device,
        gradient_accumulation_steps=cfg.train.gradient_accumulation_steps,
        num_train_epochs=cfg.train.num_epochs,
        dataloader_num_workers=cfg.train.dataloader_num_workers,
        output_dir=model_save_dir,
        logging_dir=logging_dir,
        bf16=True,
        bf16_full_eval=True,
        lr_scheduler_type=cfg.train.scheduler,
        warmup_steps=cfg.train.warmup_steps,
    )

    trainer = Trainer(
        model,
        args,
        tokenizer=tokenizer,
        train_dataset=train_dset,
        data_collator=data_collator,
    )

    trainer.train()

    # Save results
    model.save_pretrained(model_save_dir)
    tokenizer.save_pretrained(model_save_dir)
    save_path_to_hydra_logs(save_dir=model_save_dir)

    # new, untested, use at your own risk:
    trainer.state.save_to_json(model_save_dir / "trainer_state.json")


if __name__ == "__main__":
    main()
