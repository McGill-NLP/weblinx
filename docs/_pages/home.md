---
permalink: /
layout: splash
header:
    # overlay_color: rgb(237, 27, 47)
    overlay_color: rgb(180, 27, 47)
    actions:
        - label: "Paper"
          url: https://arxiv.org/abs/2402.05930
          icon: "fas fa-book"
        - label: "Dataset"
          url: "https://huggingface.co/datasets/McGill-NLP/WebLINX"
          icon: "fas fa-smile-beam"
        - label: "Explorer"
          url: "https://huggingface.co/spaces/McGill-NLP/weblinx-explorer"
          icon: "fas fa-laptop"
        - label: "Code"
          url: "https://github.com/McGill-NLP/WebLINX"
          icon: "fab fa-github"
        - label: "Tweets"
          url: "https://twitter.com/sivareddyg/status/1755799365031965140"
          icon: "fab fa-twitter"
        - label: "Models"
          url: "https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434"
          icon: "fas fa-robot"
        # - label: "Video"
        #   url: "https://youtube.com/"
        #   icon: "fas fa-video"

title: "WebLINX"
excerpt: "Real-world website navigation with multi-turn dialogue"
---

<div style="width: 90%; max-width: 900px; margin: auto; text-align: center; font-size: 18pt">
  <div style="display: flex; justify-content: space-between;">
    <a href="https://xinghanlu.com">Xing Han Lù*</a>
    <a href="https://kasnerz.github.io/">Zdeněk Kasner*</a>
    <a href="https://sivareddy.in/">Siva Reddy</a>
  </div>
  <div style="margin-top: 1em; margin-bottom: 3em"><em>*equal contribution</em></div>
</div>


<!-- Authors can be improved with pictures similar to /people -->

<img src="{{ '/assets/images/webnav.demo.svg' | relative_url }}" style="width: 90%; max-width: 900px; align-content: center; margin: auto; display: flex" alt="A diagram displaying a conversation between a navigator and instructor.">


## About WebLINX

WEBLINX is a large-scale benchmark of 100K interactions across 2300 expert demonstrations of *conversational web navigation*.
Our benchmark covers a broad range of patterns on over 150 real-world websites and can be used to train and evaluate agents in diverse scenarios.

<img loading="lazy" alt="Example of ai tasks" src="{{ '/assets/images/examples/ai.1.oyuiubm.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of booking tasks" src="{{ '/assets/images/examples/booking.1.pxtuocd.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of composing tasks" src="{{ '/assets/images/examples/composing.1.tbtnzql.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of lookup tasks" src="{{ '/assets/images/examples/lookup.1.zbrxcee.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of productivity tasks" src="{{ '/assets/images/examples/productivity.1.ytcgitj.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of shopping tasks" src="{{ '/assets/images/examples/shopping.1.wbamufj.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of social tasks" src="{{ '/assets/images/examples/social.1.xmrqcyz.webp' | relative_url }}" width="24%" height="auto">
<img loading="lazy" alt="Example of summarizing tasks" src="{{ '/assets/images/examples/summarizing.1.bctdmtt.webp' | relative_url }}" width="24%" height="auto">

## *Conversational web navigation*: What is it exactly?

We propose the problem of *conversational web navigation*, where a digital agent controls a web browser and follows user instructions to solve real-world tasks in a multi-turn dialogue fashion. To accomplish this, agents can learn from expert demonstrations, as shown below:

<div style="display: flex; justify-content: space-between; margin-bottom: 1em;">
  <video loop autoplay muted controls style="width: 72%; height: auto; margin-right: 2%;">
    <source src="{{ '/assets/videos/booking.1.vcglzhn.mp4' | relative_url }}" type="video/mp4">
    Your browser does not support the video tag.
  </video>

  <div style="width: 28%;">
    <img src="{{'/assets/images/booking.1.vcglzhn.messages.webp' | relative_url}}" style="width: 100%; height: auto;" alt="A diagram displaying a conversation between a navigator and instructor.">
  </div>
</div>

The digital agent may receive a system instruction, the HTML page, the action and conversation history, and the screenshot. The agent then needs to predict the next action to take.

<!-- 
Here, there should be a 3-column layout with the following content:
1. HTML page printed nicely using markdown. It should only have a few lines (filtered from the original HTML page to show only the relevant parts for the example)
2. The action and conversation history (preferably with nice text formatting)
3. The screenshot -->

## Can we download WebLINX now?

__[You can find our dataset on Huggingface Datasets](https://huggingface.co/datasets/McGill-NLP/weblinx)__

You can download the training, valid and test sets using the following code:

```python
from datasets import load_dataset

# Load the training, validation and test splits
train = load_dataset("McGill-NLP/weblinx", split="train")
val = load_dataset("McGill-NLP/weblinx", split="validation")
test = load_dataset("McGill-NLP/weblinx", split="test")

# Load one of the 4 out-of-domain splits (test_web, test_vis, test_geo, test_cat)
test_web = load_dataset("McGill-NLP/weblinx", split="test_web")
```

They can be directly used with LLMs or instruction-tuned text models.


## How can we explore the dataset?

We provide the WebLINX Explorer, a tool to explore the dataset and see the interactions we have collected. You can use it to take a look at the dataset before diving in.

**[Check out the WebLINX Explorer on Huggingface Spaces](https://huggingface.co/spaces/McGill-NLP/weblinx-explorer)**

<video width="100%" controls autoplay loop muted>
  <source src="{{ '/assets/videos/WeblinxExplorerDemo.webm' | relative_url }}" type="video/webm">
  Your browser does not support the video tag.
</video>

## What if I want to download the raw data (HTML, screenshots, etc.)?

If you are interested in the full data, the easiest way to download the raw dataset is the use the `huggingface_hub` library with `snapshot_download`. We show you how in the [doc's prerequisite section]({{'/docs/#prerequisites' | relative_url }}).



If you want to learn the best ways process the raw dataset (prune HTML, format history, add instructions), you can use our `weblinx` Python library. It has tons of classes and functions to help you work with the dataset and build models. You can install it using pip:

```bash
pip install weblinx
```

Please take a look at the [library documentation]({{'/docs/' | relative_url }}) for more information on how to use it.


## How can we use WebLINX to train agents?

Our agent is composed of two main components: a __Dense Markup Ranker (DMR)__ and an __action model__.

First, we convert the HTML page into a compact representation. To do this, we use a specialized model called __Dense Markup Ranker (DMR)__, which selects the most relevant elements in a HTML page, and discarding the rest.

We pass HTML, instructions, history and images to an __action model__ (which can be a LLM or a multimodal model). The *action model* generates a string that represents the next action to take (e.g. click button, inserting text in form, load new page, respond to user). That string is parsed into a structured form that can be executed.

We experiment with 19 action models, ranging from smaller models (Flan-T5-MindAct, Pix2Act) to large chat-based models (LLaMA-13B, GPT-4-turbo) and multimodal models (Fuyu-8B, GPT-4V). You can find the results in the [leaderboard]({{'/leaderboard' | relative_url }}).

<!-- There should be a card of 5 models here (MindAct, Pix2Act, Fuyu-8B, LLaMA-13B, GPT-4V) with links to the original papers of those models. -->


## Where can we find the finetuned models?

We provide the weights for the models we finetuned. You can [access them on Huggingface Hub](https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434). We will share [code to reproduce our experiments on our GitHub repository](https://github.com/mcgill-nlp/weblinx). Please note that they were finetuned for research purposes (so they are not ready for production).

## How do we use the agent to control browsers?

Our `weblinx` library lets you convert the HTML into a format that can be received by DMR or by an action model, and `weblinx` can also parse valid model outputs into a dictionary that can be converted to browser commands. 

You will need Selenium or Pupeteer to control the browser (take screenshot, grab HTML, insert unique IDs, execute action from dictionary); you can [learn selenium here](https://www.selenium.dev/documentation/webdriver/getting_started/).

## How do we cite WebLINX?

If you use our dataset, code, or models, please use the following `bibtex` citation entry:

```bibtex
@misc{lù2024weblinx,
      title={WebLINX: Real-World Website Navigation with Multi-Turn Dialogue}, 
      author={Xing Han Lù and Zdeněk Kasner and Siva Reddy},
      year={2024},
      eprint={2402.05930},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
