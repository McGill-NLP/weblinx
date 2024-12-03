<div align="center">

# WebLINX

| [**🤗Dataset**](https://huggingface.co/datasets/McGill-NLP/WebLINX) | [**📄Paper**](https://arxiv.org/abs/2402.05930) | [**🌐Website**](https://mcgill-nlp.github.io/weblinx) | [**📓Colab**](https://colab.research.google.com/github/McGill-NLP/weblinx/blob/main/examples/WebLINX_Colab_Notebook.ipynb) |
| :--: | :--: | :--: | :--: |
| [**🤖Models**](https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434) | [**💻Explorer**](https://huggingface.co/spaces/McGill-NLP/weblinx-explorer) | [**🐦Tweets**](https://twitter.com/sivareddyg/status/1755799365031965140) | [**🏆Leaderboard**](https://paperswithcode.com/sota/conversational-web-navigation-on-weblinx) |

<br>

**[WebLINX: Real-World Website Navigation with Multi-Turn Dialogue](https://mcgill-nlp.github.io/weblinx)**\
*[Xing Han Lù*](https://xinghanlu.com), [Zdeněk Kasner*](https://kasnerz.github.io/), [Siva Reddy](https://sivareddy.in)*\
_\*Equal contribution_\
**ICML 2024 (Spotlight)**

<img src="https://github.com/McGill-NLP/weblinx/raw/main/docs/assets/images/webnav.demo.svg" width="80%" alt="Sample conversation between a user and an agent" />

</div>

> [!IMPORTANT] 
> **WebLINX is now available as a benchmark through [BrowserGym](https://github.com/ServiceNow/BrowserGym), allowing you to access demonstration steps in the same way you would access a web agent environment like [WebArena](https://webarena.dev/) or [MiniWoB](https://miniwob.farama.org/index.html). This also allows you to run agents from the [Agentlab](https://github.com/ServiceNow/AgentLab) library, including agents that achieve SOTA performance through Claude-3.5-Sonnet. To enable this integration, we are releasing the `weblinx-browsergym` extension for BrowserGym on PyPi, as well as a [new dataset derived from WebLINX on Huggingface](https://huggingface.co/datasets/McGill-NLP/weblinx-browsergym).**

## Intro

Welcome to `WebLINX`'s official repository! In addition to providing code used to train [the models](https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434) reported in our [WebLINX paper](https://arxiv.org/abs/2402.05930), we also provide a comprehensive Python library (aka API) to help you work with the [WebLINX dataset](https://huggingface.co/datasets/McGill-NLP/WebLINX). 

If you want to get started with `weblinx`, please check out the following places:

| | | |
| :---: | :---: | --- |
| 🌐 | [Website](https://mcgill-nlp.github.io/weblinx) | If you want a quick overview of the project, this is the best place to start.|
| 📓 | [Colab](https://colab.research.google.com/github/McGill-NLP/weblinx/blob/main/examples/WebLINX_Colab_Notebook.ipynb) | Eager to try it out? Start by running this colab notebook!|
| 🗄️ | [Docs](https://mcgill-nlp.github.io/weblinx/docs/) | You can find quickstart instructions, the official user guide, and all relevant API specifications in the docs. |
| 📄 | [Paper](https://arxiv.org/abs/2402.05930) | If you want to get more in-depth, please read our paper, which provides comprehensive description of the project and report relevant results.|
| 🤗 | [Dataset](https://huggingface.co/datasets/McGill-NLP/WebLINX) | The official dataset page, you can download preprocessed dataset and follow instructions to get started.|
| | | |

*If you want to learn more about the codebase itself, please keep on reading!*

## Installation

```bash
# Install the base package
pip install weblinx

# Install all dependencies
pip install weblinx[all]

# Install specific dependencies for...
# ...processing HTML 🖥️
pip install weblinx[processing]
# ...video processing 📽️
pip install weblinx[video]
# ...evaluating models 🔬
pip install weblinx[eval]
# ...development of this library 🛠️
pip install weblinx[dev]
```

## Structure

This repository is structured in the following way:

| Module | Description |
| --- | --- |
| `weblinx` | The `__init__.py` provides many useful abstractions to provide a Pythonic experience when working with the dataset. For example, you can use `weblinx.Demonstration` to manipulate a demonstration at a high-level, `weblinx.Replay` to focus on more finegrained details of the demonstration, including iterating over turns, or `weblinx.Turn` to focus on a specific turn. All relevant information is included in the documentations! |
| `weblinx.eval` | Code for evaluating action models trained with WebLINX, it has both `import`able functions/metrics, but can also be accessed via command line |
| `weblinx.processing` | Code for processing various inputs or outputs used by the models, it is extensively used in the models' processing code |
| `weblinx.utils` | Miscellaneous utility functions used across the codebase. |

## Modeling

Our `modeling/` repo-level directory has code for processing, training and evaluating the models reported in the paper (DMR, LLaMA, MindAct, Pix2Act, Flan-T5). It is separate from the `weblinx` library, which focuses on data processing and evaluation. You can use it by cloning this repository, and it is recommended to edit the files in `modeling/` directly for your own needs. Our modeling code is separate from the `weblinx` library, but requires it as a dependency. You can install the modeling code by running:

```bash
# First, install the base package
pip install weblinx

# Then, clone this repo
git clone https://github.com/McGill-NLP/weblinx
cd weblinx/modeling
```

For the rest of the instructions, please take a look at the [modeling README](./modeling/README.md).

## Evaluation

To install packages necessary for evaluation, run:

```bash
pip install weblinx[eval]
```

You can now access the evaluation module by importing in Python:

```python
import weblinx.eval
```

Use `weblinx.eval.metrics` for evaluation metrics, `weblinx.eval.__init__` for useful evaluation-related functions. You may also find it useful to take a look at `weblinx.processing.outputs` to get an idea of how to use the outputs of the model for evaluation.

To run the automatic evaluation, you can use the following command:

```bash
python -m weblinx.eval --help
```

For more examples on how to use `weblinx.eval`, take a look at the [modeling README](./modeling/README.md).

> Note: We are still working on the code for `weblinx.eval` and `weblinx.processing.outputs`. If you have any questions or would like to contribute docs, please feel free to open an issue or a pull request.

## Citations

If you use this library, please cite our work using the following:
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

## License

This project's license can be found at [LICENSE](./LICENSE). Please note that the license of the data in `tests/data` follow the license from the official dataset, not the license of this repository. The official dataset's license can be found in the [official dataset page](https://huggingface.co/datasets/McGill-NLP/WebLINX). The license of the models trained using this repo might also differ - please find them in the respective model cards.
