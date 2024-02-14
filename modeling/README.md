The following instructions assume you are running from this directory (you may need to `cd` to this directory).

### Download Candidates

First, you need to download the `train.jsonl` candidate selected by `McGill-NLP/MiniLM-L6-DMR`:

```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", 
    repo_type="dataset", 
    allow_patterns="candidates/*.jsonl", 
    local_dir="./"
)
```

Download entire dataset:

```python
from huggingface_hub import snapshot_download

snapshot_download(repo_id="McGill-NLP/WebLINX-full", repo_type="dataset", local_dir="./wl_data/")

# If you only want the splits.json file, you can just run:
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", repo_type="dataset", allow_patterns="splits.json", local_dir="./wl_data/"
)

# If you only want candidates:
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", 
    repo_type="dataset", 
    allow_patterns="candidates/*.jsonl", 
    local_dir="./wl_data/"
)
```

The default configs (`config.yml`) assume that the `train.jsonl` is located at `./candidates/train.jsonl`. If you want to change the path, you need to modify the `config.yml` accordingly.

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

### Action Model: LLaMA

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


### Evaluate LLaMA

You need to specify which `eval.split` you want to evaluate on. For example, to evaluate on the `iid` split, you can run the following command:

```bash
export CUDA_VISIBLE_DEVICES="0" # Set the GPU device you want to use

# On just one split
python -m llama.eval +variant="ft_1.3b" eval.split=valid

# On multiple splits (e.g. test_iid, test_vis)
python -m llama.eval -m +variant="ft_2.7b" eval.split=test_iid,test_web,test_geo,test_cat,test_vis
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

#### Evaluate DMR

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