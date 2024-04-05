from copy import deepcopy
import json
import logging
from pathlib import Path
import random
from functools import partial

import datasets
import numpy as np
from omegaconf import OmegaConf
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import hydra
from hydra.core.hydra_config import HydraConfig
import torch
from transformers import (
    AutoTokenizer,
    TrainingArguments,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    TrainingArguments,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from tqdm import tqdm
from trl import SFTTrainer
from modeling.llama.processing import build_prompt_records_for_llama_truncated

import weblinx as wl
from weblinx.processing import load_candidate_elements
from weblinx.processing.prompt import (
    build_input_records_from_selected_turns,
    select_turns_and_candidates_for_prompts,
)
from weblinx.utils.hydra import save_path_to_hydra_logs
from weblinx.utils import set_seed

from .processing import (
    format_prompt_for_flan,
    build_formatter_for_multichoice,
)

from .processing_m2w import build_formatter_for_m2w, build_prompt_records_for_m2w


@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg):
    set_seed(cfg.seed)
    split_path = Path(cfg.data.split_path).expanduser()
    model_save_dir = Path(cfg.model.save_dir).expanduser()
    model_save_dir.mkdir(exist_ok=True, parents=True)
    logging.info(OmegaConf.to_yaml(cfg))

    tokenizer = AutoTokenizer.from_pretrained(cfg.model.tokenizer)

    demo_names = wl.utils.load_demo_names_in_split(split_path, split=cfg.train.split)
    demos = [wl.Demonstration(demo_name) for demo_name in demo_names]
    candidates = load_candidate_elements(path=cfg.candidates.train_path)

    if cfg.data.use_m2w:
        input_records_fname = "input_records_m2w.json"

        format_intent = build_formatter_for_m2w()
        build_prompt_records_fn = partial(
            build_prompt_records_for_m2w,
            format_intent=format_intent,
        )

    else:
        format_intent = build_formatter_for_multichoice()

        input_records_fname = "input_records_trunc.json"
        build_prompt_records_fn = partial(
            build_prompt_records_for_llama_truncated,
            format_intent=format_intent,
            tokenizer=tokenizer,
        )

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

    # Save the input records to the model save directory
    with open(model_save_dir.joinpath(input_records_fname), "w") as f:
        json.dump(input_records, f, indent=2)

    model = AutoModelForSeq2SeqLM.from_pretrained(
        cfg.model.name, device_map="auto", torch_dtype=torch.bfloat16
    )

    training_args = Seq2SeqTrainingArguments(
        output_dir=model_save_dir,
        optim=cfg.train.optim,
        learning_rate=cfg.train.learning_rate,
        num_train_epochs=cfg.train.num_epochs,
        per_device_train_batch_size=cfg.train.batch_size_per_device,
        gradient_accumulation_steps=cfg.train.gradient_accumulation_steps,
        gradient_checkpointing=cfg.train.gradient_checkpointing,
        warmup_steps=cfg.train.warmup_steps,
        lr_scheduler_type=cfg.train.scheduler,
        save_strategy="no",
        evaluation_strategy="no",
        logging_strategy="epoch",
        logging_first_step=True,
        prediction_loss_only=True,
        bf16=True,
        bf16_full_eval=True,
    )
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        max_length=cfg.model.max_inp_len,
    )
    train_dataset = datasets.Dataset.from_list(input_records).map(
        lambda x: tokenizer(
            x["prompt"],
            text_target=x["output_target"],
            truncation=True,
            max_length=cfg.model.max_inp_len,
        ),
        batched=True,
    )
    # Step 5: Define the Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )

    trainer.train()

    # Save model, tokenizer, trainer state, and path to hydra logs
    trainer.save_model(model_save_dir)
    tokenizer.save_pretrained(model_save_dir)
    trainer.state.save_to_json(model_save_dir / "trainer_state.json")
    save_path_to_hydra_logs(save_dir=model_save_dir)


if __name__ == "__main__":
    main()
