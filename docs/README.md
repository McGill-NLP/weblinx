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