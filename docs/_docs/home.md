---
title: "Documentation"
permalink: /docs/
sidebar:
  title: "Home"
  nav: sidebar-docs  # See /docs/_data/navigation.yml
---

If you want a simple installation, please take a look at the [`WebLINX` Huggingface Dataset](https://huggingface.co/datasets/McGill-NLP/WebLINX) -- it will show you how to download the dataset and use it with the `datasets` library.

If you want to work with the full data (containing raw files, which require more complex processing), you will find that a specialized library will be helpful. 

In this page, you can find documentation about the `WebLINX` Python library we developed for this purpose.


## Installation

To install the library, you can use pip:

```bash
pip install weblinx
```

## Prerequisites

The dataset is quite large, so you might only be interested in a subset of the data. Thus, the easiest way to download the dataset is the use the `huggingface_hub` library:

```bash
# 1. Install the library
pip install huggingface_hub[cli]
```

Here's how to use `snapshot_download` to download the dataset:

```python
from huggingface_hub import snapshot_download...

# it's possible to download the entire dataset
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", repo_type="dataset", local_dir="./wl_data"
)

# or you can download specific demos...
demo_names = ['saabwsg', 'ygprzve', 'iqaazif']  # 3 random demo from valid
patterns = [f"demonstrations/{name}/*" for name in demo_names]
snapshot_download(
    "McGill-NLP/WebLINX-full", "dataset", local_dir="./wl_data", allow_patterns=patterns
)

# ... or download all file of a certain type
patterns = ["*.json"]  # alt: ["*.json", "*.html", "*.png", "*.mp4"]
snapshot_download(
    "McGill-NLP/WebLINX-full", "dataset", local_dir="./wl_data", allow_patterns=patterns
)
```

## Using the WebLINX library

Now that you have the dataset, you can use the `weblinx` library to process the full data:

```python
from pathlib import Path
import weblinx as wl


wl_dir = Path("./wl_data")
base_dir = wl_dir / "demonstrations"
split_path = wl_dir / "splits.json"

# Load the name of the demonstrations in the training split
demo_names = wl.utils.load_demo_names_in_split(split_path, split='train')
# You can use: train, valid, test_iid, test_vis, test_cat, test_geo, test_web
# Or you can specify the demo_names yourself, such as the ones we just fetched
demo_names = ['saabwsg', 'ygprzve', 'iqaazif']  # 3 random demo from valid

# Load the demonstrations
demos = [wl.Demonstration(name, base_dir=base_dir) for name in names]

# Select a demo to work with
demo = demos[0]

# Load the Replay object, which contains the turns of the demonstration
replay = wl.Replay.from_demonstration(demo)

# Filter the turns to keep only the ones that are relevant for the task
turns = replay.filter_by_intents(
    "click", "textInput", "load", "say", "submit"
)

# Only keep the turns that have a good screenshot (i.e., the screenshot is not empty)
turns = wl.filter_turns(
    turns, lambda t: t.has_screenshot() and t.get_screenshot_status() == "good"
)

# Remove chat turns where the speaker is not the navigator (e.g. if you want to train a model to predict the next action)
turns = wl.filter_turns(
    turns,
    lambda turn: not (
        turn.type == "chat" and turn.get("speaker") != "navigator"
    ),
)
```

Let's see what it looks like:
```python
turns[::2]
```
```
[Turn(index=5, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=8, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=12, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=16, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=26, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=31, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=37, demo_name=saabwsg, base_dir=wl_data/demonstrations),
 Turn(index=41, demo_name=saabwsg, base_dir=wl_data/demonstrations)]
```

The `Turn`, `Replay`, `Demonstration` objects are designed to help you access useful parts of the data without too much effort!

For example, the `Turn` object lets you access the HTML, bounding boxes, screenshot, etc.
```python
turn = turns[0]

print("HTML sneak peak:", turn.html[:75])
print("Random Bounding Box:", turn.bboxes['bc7dcf18-542d-48e6'])
print()

# Optional: We can even get the path to the screenshot and open with Pillow
# Install Pillow with: pip install Pillow
from PIL import Image
Image.open(turn.get_screenshot_path())
```

The `Replay` object helps with working with turn-level manipulations (you can think of it as a list, and it is indexable and sliceable), whereas `wl.Demonstration` is designed to represent demonstrations at an abstract level.

```python
print("Description:", demo.form['description'])
print("Does demo have replay.json?:", demo.has_file('replay.json'))
print("When was it uploaded?:", demo.get_upload_date())
print()
print("Number of turns in replay:", replay.num_turns)
print("All intents in replay:", replay.list_intents())
print("Some URLs in replay:", replay.list_urls()[1:3])
```

```
Description: Searched in Plos Biology recently published articles and provided summary
Does demo have replay.json?: True
When was it uploaded?: 2023-06-14 10:15:59

Number of turns in replay: 48
All intents in replay: ['scroll', 'click', 'hover', 'paste', 'copy', None, 'tabswitch', 'load', 'tabcreate']
Some URLs in replay: ['https://journals.plos.org/plosbiology/', 'https://journals.plos.org/plosone/']
```

As you can see, the core `weblinx` has many useful functions to process the dataset, as well as various useful classes to represent the data (e.g. `Demonstration`, `Replay`, `Turn`). You can find more information about the library in the [documentation of the core WebLINX module]({{'/docs/core/' | relative_url }}).

You can also take a look at some useful `processing` functions in the [documentation of the processing module]({{'/docs/processing/' | relative_url }}), and some useful `utils` functions in the [documentation of the utils module]({{'/docs/utils/' | relative_url }}).


## Accessing element ranking scores

To access the elements and scores generated by the MiniLM-L6-dmr model, you can download them with:

```python
from huggingface_hub import snapshot_download
from weblinx.processing import load_candidate_elements

# Download the candidates generated by the MiniLM-L6-dmr model
snapshot_download(
    repo_id="McGill-NLP/WebLINX-full", 
    repo_type="dataset", 
    allow_patterns="candidates/*.jsonl", 
    local_dir="./wl_data/"
)

split = "train"  # or valid, test, test_geo, test_vis, test_web, test_cat 
candidates_path = f"./wl_data/candidates/{split}.jsonl"
# Access the candidates
candidates = load_candidate_elements(path=candidates_path)
```


## Examples for Training Action Model

First, make sure you have installed all the optional dependencies for the `weblinx` library:

```bash
pip install weblinx[all]
```

Then, you can use the `weblinx` library to build input records for training the model:

```python
from pathlib import Path
import weblinx as wl
from weblinx.prompt import (
    select_turns_and_candidates_for_prompts,
    build_input_records_from_selected_turns,
)
from weblinx.processing import load_candidate_elements

data_dir = Path("./wl_data")
split_path = data_dir / "splits.json"

# Load the name of the demonstrations in the training split
demo_names = wl.utils.load_demo_names_in_split(split_path, split='train')
# you can also use split='valid' or split='test-iid'

# Load the demonstrations
demos = [wl.Demonstration(name, base_dir=data_dir) for name in names]

# Load candidates generated by DMR
candidates_path = 'path/to/candidates/<split>.json'
candidates = load_candidate_elements(path=candidates_path)

def build_prompt_records_custom(*args, **kwargs):
    # Your code here
    pass

def format_prompt_custom(*args, **kwargs):
    # Your code here
    pass

# Select turns and candidates for prompting from the demonstrations
selected_turns = select_turns_and_candidates_for_prompts(
    demos=demos,
    candidates=candidates,
    num_candidates=10,
)

# Build input records for training the model
input_records = build_input_records_from_selected_turns(
    selected_turns=selected_turns,
    format_intent=format_intent,
    build_prompt_records_fn=build_prompt_records_custom,
    format_prompt_records_fn=format_prompt_custom,
)
```
