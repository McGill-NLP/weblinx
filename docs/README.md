## Docs

## Build docs

To build the docs, run this from the project root:

```bash
python docs/scripts/build_docs.py
```

It should generate new markdown files in `docs/_docs`.

## Convert images to webp

To convert images to webp, run this from the project root:

```bash
# convert docs/assets/images/examples
python docs/scripts/convert_to_webp.py  -d docs/assets/images/examples --height 400
```

## Run

The weblinx homepage is built with jekyll, which uses ruby. If you do not have ruby installed, please install it, then install bundler:
```bash
# Install ruby and gem
sudo apt-get install ruby-dev

# install bundler
gem install bundler -v 2.4.22
```

to run it locally, run this from the project root:

```bash
cd docs
bundle install
bundle exec jekyll serve
```