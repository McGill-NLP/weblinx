<div align="center">

# WebLINX

| [**🤗Dataset**](https://huggingface.co/datasets/McGill-NLP/WebLINX) | [**📄Paper**](https://arxiv.org/abs/2402.05930) | [**🌐Website**](https://mcgill-nlp.github.io/weblinx) |
| :--: | :--: | :--: |
| [**🤖Models**](https://huggingface.co/collections/McGill-NLP/weblinx-models-65c57d4afeeb282d1dcf8434) | [**💻Explorer**](https://huggingface.co/spaces/McGill-NLP/weblinx-explorer) | [**🐦Tweets**](https://twitter.com/sivareddyg/status/1755799365031965140) |


> **[WebLINX: Real-World Website Navigation with Multi-Turn Dialogue](https://mcgill-nlp.github.io/weblinx)**\
> *[Xing Han Lù*](https://xinghanlu.com), [Zdeněk Kasner*](https://kasnerz.github.io/), [Siva Reddy](https://sivareddy.in)*\
> _\*Equal contribution_

<img src="./assets/webnav.demo.svg" width="80%" alt="Sample conversation between a user and an agent" />

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

Coming soon!
