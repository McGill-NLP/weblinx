The following instructions assume you are running from this directory (you may need to `cd` to this directory).

### Download Data

First, you need to download the `splits.json` file containing information about all the splits, as well as the `train.jsonl` candidate selected by `McGill-NLP/MiniLM-L6-DMR`:

```python
from huggingface_hub import snapshot_download

# splits.json
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", repo_type="dataset", allow_patterns="splits.json", local_dir="./wl_data/"
)

# candidates files
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", 
    repo_type="dataset", 
    allow_patterns="candidates/*.jsonl", 
    local_dir="./wl_data/"
)
```

Download the full dataset (warning: this will take a while):

```python
from huggingface_hub import snapshot_download

snapshot_download(repo_id="McGill-NLP/WebLINX-full", repo_type="dataset", local_dir="./wl_data/")
```

The default configs (`llama/conf/config.yml`) assume that the `train.jsonl` is located at `./wl_data/candidates/train.jsonl`. If you want to change the path, you need to modify the `config.yml` accordingly.

### Set `WEBLINX_PROJECT_DIR`

You need to set the `WEBLINX_PROJECT_DIR` environment variable to the root directory of the WebLINX project. For example, if you have the following directory structure:

```bash
export WEBLINX_PROJECT_DIR=/path/to/the/modeling/directory/

# For example, if you are in the modeling directory, you can run:
export WEBLINX_PROJECT_DIR=$(pwd)
```

### Install Dependencies

You need to install the dependencies by running the following command:

```bash
pip install -r requirements.txt
```

However, due to `flash-attention` requiring `torch` to be pre-installed, it has to be install right after everything else has been installed:
```bash
# Regular install
pip install "flash-attn>=2.3.0"
# IF you have limited RAM, you can try this:
MAX_JOBS=4 pip install "flash-attn>=2.3.0" --no-build-isolation
# If you have issues with nvcc, try this:
FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE pip install "flash-attn>=2.3.0" --no-build-isolation
```

### Dense Markup Ranking (DMR)

#### Train DMR

You can train the model by running the following command (it will automatically use the hydra config from `conf/`):

```bash
export CUDA_VISIBLE_DEVICES="0" # Set the GPU device you want to use

# Finetune MiniLM-L6-DMR (Default)
python -m dmr.train

# Finetune variant gte or bge
python -m dmr.train +variant=gte
python -m dmr.train +variant=bge
```

Results will be saved in `./results` and checkpoints in `./checkpoints`.

#### Inference for DMR

You need to specify which `eval.split` you want to evaluate on. For example, to evaluate on the `iid` split, you can run the following command:

```bash
export CUDA_VISIBLE_DEVICES="0" # Set the GPU device you want to use

# On just one
python -m dmr.eval eval.split=valid

# On multiple splits (e.g. test_iid, test_vis)
python -m dmr.eval eval.split=test_iid,test_web,test_geo,test_cat,test_vis

# Or for bge, gte
python -m dmr.eval +variant=gte eval.split=test_iid,test_web,test_geo,test_cat,test_vis
python -m dmr.eval +variant=bge eval.split=test_iid,test_web,test_geo,test_cat,test_vis
```

### Action Model

#### Train LLaMA

You can train the model by running the following command (it will automatically use the hydra config from `conf/`):

```bash
export CUDA_VISIBLE_DEVICES="0" # Set the GPU device you want to use

# Finetune 1.3b variant
python -m llama.train +variant="ft_1.3b"

# Finetune 2.7b variant
python -m llama.train +variant="ft_2.7b"

# For 7b, you will need to use fsdp in accelerate to train on 4 GPUs with 48GB VRAM
export CUDA_VISIBLE_DEVICES="0,1,2,3"
accelerate launch --use_fsdp --config_file llama/accelerate/fsdp_7b.yaml -m llama.train +variant="ft_7b"

# For 13b, you need 6 GPUs with 48GB VRAM
export CUDA_VISIBLE_DEVICES="0,1,2,3,4,5"
accelerate launch --use_fsdp --config_file llama/accelerate/fsdp_13b.yaml -m llama.train +variant="ft_13b"
```

Results will be saved in `./results` and checkpoints in `./checkpoints`.


#### Run LLaMA on Evaluation Splits

You need to specify which `eval.split` you want to evaluate on. For example, to evaluate on the `iid` split, you can run the following command:

```bash
export CUDA_VISIBLE_DEVICES="0" # Set the GPU device you want to use

# On just one split
python -m llama.eval +variant="ft_1.3b" eval.split=valid

# On multiple splits (e.g. test_iid, test_vis)
python -m llama.eval -m +variant="ft_2.7b" eval.split=test_iid,test_web,test_geo,test_cat,test_vis
```

### Evaluation

To run the evaluation metrics, you can use the following command (from this directory):

```bash
python -m weblinx.eval -d results -b ./wl_data/demonstrations
```

In this case, `-b` is the base directory for the demonstrations, and `-d` is the directory containing the results (generated above by the `llama.eval` script). This will automatically run the evaluation metrics and save the results in the `results/aggregated_scores.json` directory. If you are only interested in the overall score for a split (e.g. `valid`), you can find look for the following entry in the aggregated score file (as an example):

```json
// ...
  {
    "split": "valid",
    "intent": "overall",
    "metric": "overall",
    "model_name": "princeton-nlp/Sheared-LLaMA-1.3B",
    "project_name": "llama_ft",
    "score": 0.21667765869744438,
    "unconditional_score": 0.15307513104251605
  },
// ...
```

Behind the scene, this will use the `weblinx.eval.auto_eval_and_save` function to run the evaluation metrics. If you want more control, you can also use that `weblinx.eval.auto_eval_and_save` function directly if you prefer; for an example, check out `weblinx/eval/__main__.py`.

Note that it might be slow the first time you run, because it reads a lot of demonstrations and load millions of files. However, a demo-level cache is automatically created (see `./.cache/demonstrations`), so the next time you run it, it should be much faster.