<div align="center">

# WebLINX

| [**🤗Dataset**](https://huggingface.co/datasets/McGill-NLP/WebLINX) | [**📄Paper**](https://arxiv.org/abs/2402.05930) | [**🌐Website**](https://mcgill-nlp.github.io/weblinx) | [**📓Colab**](https://colab.research.google.com/github/McGill-NLP/weblinx/blob/main/examples/WebLINX_Colab_Notebook.ipynb) |
| :--: | :--: | :--: | :--: |
| [**🤖Models**](https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434) | [**💻Explorer**](https://huggingface.co/spaces/McGill-NLP/weblinx-explorer) | [**🐦Tweets**](https://twitter.com/sivareddyg/status/1755799365031965140) | [**🏆Leaderboard**](https://paperswithcode.com/sota/conversational-web-navigation-on-weblinx) |


> **[WebLINX: Real-World Website Navigation with Multi-Turn Dialogue](https://mcgill-nlp.github.io/weblinx)**\
> *[Xing Han Lù*](https://xinghanlu.com), [Zdeněk Kasner*](https://kasnerz.github.io/), [Siva Reddy](https://sivareddy.in)*\
> _\*Equal contribution_

<img src="https://github.com/McGill-NLP/weblinx/raw/main/docs/assets/images/webnav.demo.svg" width="80%" alt="Sample conversation between a user and an agent" />

</div>

### Installation

```bash
# Install the base package
pip install weblinx

# Install all dependencies
pip install weblinx[all]

# Install specific dependencies for...
# ...processing HTML
pip install weblinx[processing]
# ...video processing
pip install weblinx[video]
# ...development
pip install weblinx[dev]
```

### Library Usage

Check out our [documentation](https://mcgill-nlp.github.io/weblinx/docs) for more information on how to use WebLINX.


### Modeling

Our modeling code is separate from the `weblinx` library, but requires it as a dependency. You can install the modeling code by running:

```bash
# First, install the base package
pip install weblinx

# THen, clone this repo
git clone https://github.com/McGill-NLP/weblinx
cd weblinx/modeling
```

For the rest of the instructions, please take a look at the [modeling README](./modeling/README.md).

### Evaluation

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

### Citations

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
